import requests
from bs4 import BeautifulSoup
from datetime import datetime

# URLs
LOGIN_URL = "http://127.0.0.1:8000/login"
LEDGER_URL = "http://127.0.0.1:8000/ledger"
CAISSA_API = "http://127.0.0.1:5000/ledger"

# Credentials
USERNAME = "admin"
PASSWORD = "password"

# Helper: clean up date formats into YYYY-MM-DD
def normalize_date(date_str):
    formats = ["%Y-%m-%d", "%d-%b-%Y", "%Y/%m/%d"]  # different formats in Private I
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str  # fallback if unknown

# Helper: clean up amounts (remove commas, convert to float)
def normalize_amount(amount_str):
    return float(amount_str.replace(",", ""))

# Step 1: Start a session and log in
session = requests.Session()
login_data = {"username": USERNAME, "password": PASSWORD}
resp = session.post(LOGIN_URL, data=login_data)

if resp.url.endswith("/ledger"):
    print("✅ Logged in successfully to Private I dummy")
else:
    print("❌ Login failed")
    exit()

# Step 2: Scrape all ledger pages
page = 1
while True:
    print(f"📄 Fetching ledger page {page}...")
    resp = session.get(LEDGER_URL, params={"page": page})
    soup = BeautifulSoup(resp.text, "html.parser")

    table = soup.find("table")
    if not table:
        print("⚠️ No table found. Stopping.")
        break

    rows = table.find_all("tr")[1:]  # skip the header row
    if not rows:
        print("⚠️ No more rows found. Stopping.")
        break

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        entry = {
            "date": normalize_date(cols[0]),
            "description": cols[1],
            "amount": normalize_amount(cols[2]),
            "currency": cols[3],
            "fund": cols[4],
        }

        # Send to Caissa
        r = requests.post(CAISSA_API, json=entry)
        if r.status_code == 201:
            print(f"   ✅ Added entry: {entry}")
        else:
            print(f"   ❌ Failed to add: {entry} | {r.status_code}")

    page += 1
