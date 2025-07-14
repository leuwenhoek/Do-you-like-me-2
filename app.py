from flask import Flask, request, redirect, render_template, url_for, session
import sqlite3
import datetime
import os

app = Flask(__name__)
app.secret_key = "very-very-secret"

PATH = "/tmp/database.db"
print("Database path:", PATH)

def db():
    conn = sqlite3.connect(PATH)
    curr = conn.cursor()
    curr.execute('''
        CREATE TABLE IF NOT EXISTS response(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            opinion TEXT NOT NULL,
            description TEXT NOT NULL,
            reason TEXT NOT NULL,
            connection TEXT NOT NULL,
            irritating TEXT NOT NULL,
            improvements TEXT NOT NULL,
            date DATE DEFAULT (DATE('now')),
            time TIME DEFAULT (TIME('now'))
        )
    ''')
    conn.commit()
    conn.close()

# Call db() here so the DB/table is created on every startup, even on Render
db()

@app.route("/", methods=["POST", "GET"])
def main():
    return redirect(url_for("formfun"))

@app.route("/form", methods=["POST", "GET"])
def formfun():
    if request.method == "POST":
        session["name"] = name = request.form.get("name")
        session["opinion"] = opinion = request.form.get("opinion")
        session["description"] = description = request.form.get("description")
        session["reason"] = reason = request.form.get("reason")
        session["connection"] = connection = request.form.get("connection")
        session["irritating"] = irritating = request.form.get("irritating")
        session["improvements"] = improvements = request.form.get("improvements")

        current_time = datetime.datetime.utcnow().strftime("%H:%M:%S")

        conn = sqlite3.connect(PATH)
        curr = conn.cursor()
        curr.execute('''
            INSERT INTO response
            (name, opinion, description, reason, connection, irritating, improvements, time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, opinion, description, reason, connection, irritating, improvements, current_time))
        conn.commit()
        conn.close()

        return redirect(url_for("checkfun"))

    return render_template("index.html")

# ...rest of your routes...

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
