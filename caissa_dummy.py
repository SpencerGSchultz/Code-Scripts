from flask import Flask, request, jsonify, render_template_string, redirect, url_for

app = Flask(__name__)
ledger_entries = []  # starts empty

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Caissa Ledger</title>
</head>
<body>
    <h1>Caissa Ledger (Dummy)</h1>
    <form method="POST" action="/reset">
        <button type="submit" style="margin-bottom:20px; padding:10px; background-color:red; color:white; border:none; cursor:pointer;">
            🔄 Reset Ledger
        </button>
    </form>
    <table border="1" cellpadding="5">
        <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Amount</th>
            <th>Currency</th>
            <th>Fund</th>
        </tr>
        {% for entry in ledger %}
        <tr>
            <td>{{ entry["date"] }}</td>
            <td>{{ entry["description"] }}</td>
            <td>{{ entry["amount"] }}</td>
            <td>{{ entry["currency"] }}</td>
            <td>{{ entry["fund"] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, ledger=ledger_entries)

@app.route("/ledger", methods=["POST"])
def add_entry():
    data = request.json
    ledger_entries.append(data)
    return jsonify({"status": "success", "entry_added": data}), 201

@app.route("/ledger", methods=["GET"])
def get_ledger():
    return jsonify(ledger_entries)

# New reset route
@app.route("/reset", methods=["POST"])
def reset_ledger():
    ledger_entries.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
