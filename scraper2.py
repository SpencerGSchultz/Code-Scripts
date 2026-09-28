import requests
from bs4 import BeautifulSoup
from datetime import datetime

# URLs
LOGIN_URL = "http://127.0.0.1:8000/login"
TRANSACTIONS_URL = "http://127.0.0.1:8000/transactions"
CAISSA_API = "http://127.0.0.1:5000/ledger"

# Credentials
USERNAME = "admin"
PASSWORD = "password"

# Helper: clean up dates into YYYY-MM-DD
def normalize_date(date_str):
    formats = ["%Y-%m-%d", "%Y/%m/%d", "%d-%b-%Y", "%d/%m/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str

# Helper: clean up amounts (remove commas, convert to float)
def normalize_amount(amount_str):
    return float(amount_str.replace(",", "").replace("(", "-").replace(")", ""))

# Step 1: Log into Private I
session = requests.Session()
login_data = {"username": USERNAME, "password": PASSWORD}
resp = session.post(LOGIN_URL, data=login_data)

if resp.url.endswith("/transactions"):
    print("✅ Logged in successfully to Private I dummy")
else:
    print("❌ Login failed")
    exit()

# Step 2: Scrape all transaction pages
page = 1
while True:
    print(f"📄 Fetching transactions page {page}...")
    resp = session.get(TRANSACTIONS_URL, params={"page": page})
    soup = BeautifulSoup(resp.text, "html.parser")

    table = soup.find("table")
    if not table:
        print("⚠️ No table found. Stopping.")
        break

    rows = table.find_all("tr")[1:]  # skip header row
    if not rows:
        print("⚠️ No more rows found. Stopping.")
        break

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) < 6:
            continue  # skip malformed rows

        privatei_entry = {
            "transaction_id": cols[0],
            "date": normalize_date(cols[1]),
            "fund": cols[2],
            "type": cols[3],
            "ccy": cols[4],
            "amount": normalize_amount(cols[5]),
        }

        # Map to Caissa format
        caissa_entry = {
            "date": privatei_entry["date"],  # effective date
            "description": privatei_entry["type"],  # type
            "amount": privatei_entry["amount"],
            "currency": privatei_entry["ccy"],
            "fund": privatei_entry["fund"],  # ledger
        }

        # Send to Caissa
        r = requests.post(CAISSA_API, json=caissa_entry)
        if r.status_code == 201:
            print(f"   ✅ Added entry: {caissa_entry}")
        else:
            print(f"   ❌ Failed to add: {caissa_entry} | {r.status_code}")

    page += 1
