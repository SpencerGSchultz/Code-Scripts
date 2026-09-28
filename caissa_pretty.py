from flask import Flask, jsonify, request, session, render_template_string, redirect, url_for
from datetime import datetime
app = Flask(__name__)
app.secret_key = "caissa_secret_key"

# In-memory ledger data
ledger_entries = []

# ---------- HTML Dashboard (realistic Caissa style) ----------
CAISSA_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Caissa – Ledger Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {
      --accent: #0b8f8a;
      --accent-dark: #066b66;
      --bg: #f5f7f7;
      --card: #ffffff;
      --muted: #6b7280;
    }
    html, body { margin:0; height:100%; font-family: Inter, "Segoe UI", Arial, sans-serif; background:var(--bg); color:#111; }
    .sidebar { width:220px; background:linear-gradient(180deg,var(--accent),var(--accent-dark)); color:white; padding:20px 16px; box-sizing:border-box; display:flex; flex-direction:column; gap:20px; min-height:100vh; }
    .logo { font-weight:700; font-size:18px; }
    .main { flex:1; padding:20px; }
    .app { display:flex; min-height:100vh; }
    .card { background:var(--card); border-radius:10px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.05); border:1px solid #e0e6e6; }
    .btn { background:var(--accent); color:white; border:none; padding:8px 12px; border-radius:6px; cursor:pointer; font-weight:600; }
    .btn.ghost { background:transparent; color:var(--accent-dark); border:1px solid #cfe5e5; }
    table { width:100%; border-collapse:collapse; font-size:14px; margin-top:10px; }
    thead th { background:#f1f5f5; text-align:left; padding:10px; font-weight:700; border-bottom:1px solid #dde6e6; }
    tbody td { padding:10px; border-bottom:1px solid #e8efef; }
    tbody tr:nth-child(even) td { background:#fafdfd; }
    .amount { text-align:right; }
    .muted { color:var(--muted); font-size:13px; }
    .topbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:18px; }
    input[type="search"]{ padding:6px 8px; border:1px solid #dde5e5; border-radius:6px; min-width:220px; }
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <div class="logo">Caissa Dummy</div>
      <div class="muted">Admin Dashboard</div>
      <div style="flex:1"></div>
      <form method="POST" action="/logout">
        <button class="btn ghost">Logout</button>
      </form>
    </aside>

    <main class="main">
      <div class="topbar">
        <h2>Ledger Overview</h2>
        <div>
          <form method="POST" action="/reset" style="display:inline;">
            <button class="btn ghost">Reset Ledger</button>
          </form>
          <button class="btn" onclick="window.location.reload()">Refresh</button>
        </div>
      </div>

      <div class="card">
        <form method="GET" style="margin-bottom:12px;">
          <input type="search" name="q" placeholder="Search fund, date or description..." value="{{ q|default('') }}">
          <button class="btn ghost">Filter</button>
        </form>

        {% if ledger|length == 0 %}
          <p class="muted">No ledger entries yet. Use your scraper to POST data to <code>/ledger</code>.</p>
        {% else %}
          <table>
            <thead>
              <tr><th>Date</th><th>Description</th><th class="amount">Amount</th><th>Currency</th><th>Fund</th></tr>
            </thead>
            <tbody>
              {% for e in ledger %}
              <tr>
                <td>{{ e['date'] }}</td>
                <td>{{ e['description'] }}</td>
                <td class="amount">{{ "{:,.2f}".format(e['amount']) }}</td>
                <td>{{ e['currency'] }}</td>
                <td>{{ e['fund'] }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        {% endif %}
      </div>
    </main>
  </div>
</body>
</html>
"""

# ---------- LOGIN PAGE ----------
LOGIN_TEMPLATE = """
<!doctype html>
<html><head><title>Caissa Dummy Login</title>
<style>
  body { font-family:Inter, Arial, sans-serif; background:#f5f7f7; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; }
  .box { background:white; padding:32px; border-radius:10px; box-shadow:0 2px 12px rgba(0,0,0,0.1); width:300px; }
  input { width:100%; margin-top:8px; padding:10px; border:1px solid #ccc; border-radius:6px; }
  button { width:100%; margin-top:14px; background:#0b8f8a; color:white; border:none; padding:10px; border-radius:6px; cursor:pointer; }
  button:hover{ background:#087a75; }
  .error { color:red; margin-top:10px; font-size:14px; text-align:center; }
</style></head>
<body>
  <div class="box">
    <h2>Caissa Dummy</h2>
    <form method="POST">
      <label>Username</label><input name="username" required>
      <label>Password</label><input type="password" name="password" required>
      <button type="submit">Login</button>
      {% if error %}<div class="error">{{ error }}</div>{% endif %}
    </form>
  </div>
</body></html>
"""

# ---------- ROUTES ----------
@app.route("/", methods=["GET"])
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    q = request.args.get("q", "").lower()
    data = ledger_entries
    if q:
        data = [e for e in ledger_entries if q in e["description"].lower() or q in e["fund"].lower()]
    return render_template_string(CAISSA_TEMPLATE, ledger=data, q=q)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u == "caissa" and p == "demo123":
            session["logged_in"] = True
            return redirect(url_for("home"))
        return render_template_string(LOGIN_TEMPLATE, error="Invalid credentials")
    return render_template_string(LOGIN_TEMPLATE, error=None)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/ledger", methods=["POST"])
def add_ledger():
    """Scraper POSTs JSON here"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400
    entry = {
        "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
        "description": data.get("description", "Unknown"),
        "amount": float(data.get("amount", 0)),
        "currency": data.get("currency", "USD"),
        "fund": data.get("fund", "N/A"),
    }
    ledger_entries.append(entry)
    return jsonify({"status": "added", "entry": entry}), 201

@app.route("/ledger", methods=["GET"])
def get_ledger():
    """Return ledger as JSON"""
    return jsonify(ledger_entries)

@app.route("/reset", methods=["POST"])
def reset_ledger():
    ledger_entries.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)

#Username: caissa
#Password: demo123