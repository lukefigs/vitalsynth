
from flask import Flask, request, jsonify
import csv
import os

app = Flask(__name__)
LEADS_FILE = "leads.csv"

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "Missing email"}), 400

    file_exists = os.path.isfile(LEADS_FILE)
    with open(LEADS_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["email"])
        writer.writerow([email])

    return jsonify({"message": "Lead captured"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
