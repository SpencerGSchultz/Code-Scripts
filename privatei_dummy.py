from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "dummy_secret"  # needed for sessions

# Example ledger data (20 rows to simulate multiple pages)
ledger_data = [
    {"date": "2025-01-15", "description": "Capital Call", "amount": "100,000", "currency": "USD", "fund": "Fund A"},
    {"date": "2025-02-10", "description": "Management Fee", "amount": "-5,000", "currency": "USD", "fund": "Fund A"},
    {"date": "2025-03-05", "description": "Distribution", "amount": "20,000", "currency": "USD", "fund": "Fund A"},
    {"date": "15-Apr-2025", "description": "Capital Call", "amount": "75,000", "currency": "USD", "fund": "Fund B"},
    {"date": "2025/05/20", "description": "Distribution", "amount": "15,000", "currency": "USD", "fund": "Fund B"},
    {"date": "2025-06-15", "description": "Capital Call", "amount": "50,000", "currency": "USD", "fund": "Fund C"},
    # duplicate rows to simulate more data
] * 4  # makes ~24 rows for pagination

ROWS_PER_PAGE = 10

# Login page template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <h1>Private I Dummy - Login</h1>
    <form method="POST" action="/login">
        <label>Username:</label><input type="text" name="username"><br><br>
        <label>Password:</label><input type="password" name="password"><br><br>
        <button type="submit">Login</button>
    </form>
</body>
</html>
"""

# Ledger page template with pagination
LEDGER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Private I - Ledger</title>
</head>
<body>
    <h1>Ledger Entries</h1>
    <table border="1" cellpadding="5">
        <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Amount</th>
            <th>Currency</th>
            <th>Fund</th>
        </tr>
        {% for row in page_data %}
        <tr>
            <td>{{ row["date"] }}</td>
            <td>{{ row["description"] }}</td>
            <td>{{ row["amount"] }}</td>
            <td>{{ row["currency"] }}</td>
            <td>{{ row["fund"] }}</td>
        </tr>
        {% endfor %}
    </table>

    <br>
    <div>
        {% if page > 1 %}
            <a href="/ledger?page={{ page - 1 }}">Previous</a>
        {% endif %}
        Page {{ page }}
        {% if end_index < total_rows %}
            <a href="/ledger?page={{ page + 1 }}">Next</a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("ledger"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Dummy login check
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "password":
            session["logged_in"] = True
            return redirect(url_for("ledger"))
        else:
            return "❌ Invalid login. Try again."
    return LOGIN_TEMPLATE

@app.route("/ledger")
def ledger():
    if "logged_in" not in session:
        return redirect(url_for("login"))

    page = int(request.args.get("page", 1))
    start_index = (page - 1) * ROWS_PER_PAGE
    end_index = start_index + ROWS_PER_PAGE
    page_data = ledger_data[start_index:end_index]

    return render_template_string(
        LEDGER_TEMPLATE,
        page_data=page_data,
        page=page,
        total_rows=len(ledger_data),
        end_index=end_index
    )

if __name__ == "__main__":
    app.run(port=8000, debug=True)
