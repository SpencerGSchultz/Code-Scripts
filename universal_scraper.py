import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
from pathlib import Path
import sys   # <-- NEW (to read command-line arguments)


# --------------------------
# STEP 1: Helpers to clean data
# --------------------------
def normalize_date(date_str):
    formats = ["%Y-%m-%d", "%d-%b-%Y", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str

def normalize_amount(amount_str):
    amt = str(amount_str).replace(",", "").replace("(", "-").replace(")", "")
    try:
        return float(amt)
    except ValueError:
        return 0.0


# --------------------------
# STEP 2: Login (only if needed)
# --------------------------
def login(session, config):
    if "login_url" in config["source"]:
        creds = {
            "username": config["source"].get("username"),
            "password": config["source"].get("password"),
        }
        print(f"🔑 Logging in to {config['source']['name']}...")
        return session.post(config["source"]["login_url"], data=creds)
    return None


# --------------------------
# STEP 3: Scrape HTML tables
# --------------------------
def scrape_html(session, config):
    page = 1
    while True:
        params = {}
        if "pagination_param" in config["source"]:
            params[config["source"]["pagination_param"]] = page

        r = session.get(config["source"]["transactions_url"], params=params)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table")
        if not table:
            break

        rows = table.find_all("tr")[1:]  # skip headers
        if not rows:
            break

        for row in rows:
            yield [c.get_text(strip=True) for c in row.find_all("td")]

        page += 1


# --------------------------
# STEP 4: Scrape JSON APIs
# --------------------------
def scrape_api(session, config):
    url = config["source"]["transactions_url"]
    r = session.get(url)
    data = r.json()

    for record in data:
        yield record


# --------------------------
# STEP 5: Decide which scraper to use
# --------------------------
def scrape_source(session, config):
    stype = config["source"].get("type", "html")
    if stype == "html":
        return scrape_html(session, config)
    elif stype == "api":
        return scrape_api(session, config)
    else:
        raise ValueError(f"Unsupported source type: {stype}")


# --------------------------
# STEP 6: Normalize entries
# --------------------------
def normalize_entry(raw, config):
    mapping = config["source"]["columns"]
    entry = {}

    if isinstance(raw, list):  # HTML row
        col_names = list(mapping.keys())
        raw_dict = {col_names[i]: raw[i] for i in range(len(raw))}
    elif isinstance(raw, dict):  # JSON API
        raw_dict = raw
    else:
        raw_dict = {}

    for source_col, target_col in mapping.items():
        value = raw_dict.get(source_col, "")

        if "date" in target_col.lower():
            entry[target_col] = normalize_date(value)
        elif "amount" in target_col.lower():
            entry[target_col] = normalize_amount(value)
        else:
            entry[target_col] = value

    return entry


# --------------------------
# STEP 7: Send to target
# --------------------------
def post_to_target(entry, config):
    target = config["target"]

    if "api_url" in target:
        r = requests.post(target["api_url"], json=entry)
        return r.status_code == 201

    elif "file_path" in target:
        file_path = Path(target["file_path"])
        write_header = not file_path.exists()
        with open(file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=entry.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(entry)
        return True

    else:
        print("⚠️ No valid target defined")
        return False


# --------------------------
# STEP 8: Main driver
# --------------------------
def run_scraper(config_path="config.json"):
    with open(config_path) as f:
        config = json.load(f)

    session = requests.Session()
    if "login_url" in config["source"]:
        login(session, config)

    print(f"🔍 Scraping from {config['source']['name']}...")
    records = scrape_source(session, config)

    for raw in records:
        entry = normalize_entry(raw, config)
        success = post_to_target(entry, config)
        if success:
            print(f"✅ Added entry: {entry}")
        else:
            print(f"❌ Failed to add: {entry}")


# --------------------------
# STEP 9: Run from command line
# --------------------------
if __name__ == "__main__":
    # Example: python universal_scraper.py config_privatei.json
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "config.json"  # fallback if no argument
    run_scraper(config_file)
