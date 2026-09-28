from flask import Flask, request, jsonify, render_template_string, redirect, url_for

app = Flask(__name__)
ledger_entries = []  # starts empty

LEDGER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Caissa Dummy - Ledgers</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 6px; text-align: left; }
        th { background-color: #f2f2f2; }
        h1 { margin-bottom: 10px; }
    </style>
</head>
<body>
    <h1>Caissa Dummy - Ledgers</h1>
    <form method="POST" action="/reset">
        <button type="submit" style="margin-bottom:20px; padding:8px; background-color:red; color:white; border:none; cursor:pointer;">
            🔄 Reset Ledger
        </button>
    </form>
    <table>
        <tr>
            <th>Effective Date</th>
            <th>Sent/Received Date</th>
            <th>Ledger</th>
            <th>Amount (USD)</th>
            <th>Type</th>
            <th>Pending</th>
        </tr>
        {% for entry in ledger %}
        <tr>
            <td>{{ entry["date"] }}</td>
            <td>{{ entry["date"] }}</td>
            <td>{{ entry["fund"] }}</td>
            <td style="text-align:right;">{{ entry["amount"] }}</td>
            <td>{{ entry["description"] }}</td>
            <td><input type="checkbox"></td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(LEDGER_TEMPLATE, ledger=ledger_entries)

@app.route("/ledger", methods=["POST"])
def add_entry():
    data = request.json
    ledger_entries.append(data)
    return jsonify({"status": "success", "entry_added": data}), 201

@app.route("/ledger", methods=["GET"])
def get_ledger():
    return jsonify(ledger_entries)

@app.route("/reset", methods=["POST"])
def reset():
    ledger_entries.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(port=5000, debug=True)
