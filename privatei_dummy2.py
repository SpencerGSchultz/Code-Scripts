from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "dummy_secret"  # needed for sessions

# Example transaction data (duplicated for pagination realism)
transactions = [
    {"id": 205803614, "date": "2026-01-04", "fund": "RTW Offshore Fund One Ltd", "type": "Redemption", "ccy": "USD", "amount": "1,919,241.80"},
    {"id": 205803612, "date": "2026-01-04", "fund": "Investors' Capital", "type": "Contribution", "ccy": "USD", "amount": "1,919,241.80"},
    {"id": 205803606, "date": "2026-01-01", "fund": "Investors' Capital", "type": "Capital Outflow", "ccy": "USD", "amount": "1,919,241.80"},
    {"id": 270642445, "date": "2025-10-08", "fund": "M3 Ventures IV", "type": "Investment Call", "ccy": "USD", "amount": "550,000.00"},
    {"id": 268677730, "date": "2025-10-06", "fund": "Genstar Capital Partners IX", "type": "Management Fee", "ccy": "USD", "amount": "26,982.17"},
    {"id": 268677724, "date": "2025-10-03", "fund": "Genstar Capital Partners XI", "type": "Partnership Expenses", "ccy": "USD", "amount": "70,593.11"},
] * 4  # duplicate for realism

ROWS_PER_PAGE = 10

# Login page
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Private I Dummy - Login</title></head>
<body style="font-family: Arial; margin: 40px;">
    <h2>Private I Dummy - Login</h2>
    <form method="POST" action="/login">
        <label>Username:</label><input type="text" name="username"><br><br>
        <label>Password:</label><input type="password" name="password"><br><br>
        <button type="submit">Login</button>
    </form>
</body>
</html>
"""

# Transactions page
TRANSACTIONS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Private I Dummy - Transactions</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 6px; text-align: left; }
        th { background-color: #f2f2f2; }
        h1 { margin-bottom: 10px; }
    </style>
</head>
<body>
    <h1>Transactions</h1>
    <table>
        <tr>
            <th>Transaction ID</th>
            <th>Date</th>
            <th>Fund/Account</th>
            <th>Transaction Type</th>
            <th>CCY</th>
            <th>Amount</th>
        </tr>
        {% for tx in page_data %}
        <tr>
            <td>{{ tx["id"] }}</td>
            <td>{{ tx["date"] }}</td>
            <td>{{ tx["fund"] }}</td>
            <td>{{ tx["type"] }}</td>
            <td>{{ tx["ccy"] }}</td>
            <td style="text-align:right;">{{ tx["amount"] }}</td>
        </tr>
        {% endfor %}
    </table>
    <br>
    <div>
        {% if page > 1 %}
            <a href="/transactions?page={{ page - 1 }}">Previous</a>
        {% endif %}
        Page {{ page }}
        {% if end_index < total %}
            <a href="/transactions?page={{ page + 1 }}">Next</a>
        {% endif %}
    </div>
</body>
</html>
"""

# Home route
@app.route("/")
def home():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("transactions_view"))  # ✅ fixed endpoint name

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "password":
            session["logged_in"] = True
            return redirect(url_for("transactions_view"))  # ✅ fixed endpoint name
        else:
            return "❌ Invalid login"
    return LOGIN_TEMPLATE

# Transactions route
@app.route("/transactions")
def transactions_view():
    if "logged_in" not in session:
        return redirect(url_for("login"))

    page = int(request.args.get("page", 1))
    start_index = (page - 1) * ROWS_PER_PAGE
    end_index = start_index + ROWS_PER_PAGE
    page_data = transactions[start_index:end_index]

    return render_template_string(
        TRANSACTIONS_TEMPLATE,
        page_data=page_data,
        page=page,
        end_index=end_index,
        total=len(transactions)
    )

if __name__ == "__main__":
    app.run(port=8000, debug=True)
