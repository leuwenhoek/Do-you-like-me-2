from flask import Flask, request, redirect, render_template, url_for, session
import sqlite3
import datetime
import os

app = Flask(__name__)
app.secret_key = "very-very-secret"

PATH = "/tmp/database.db"
print("Database path:", PATH)


db_dir = os.path.dirname(PATH)
if not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

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

        # Use current UTC time string for insertion
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

@app.route("/check", methods=["POST", "GET"])
def checkfun():
    name_ = session.get("name")
    description_ = session.get("description")
    improvements_ = session.get("improvements")
    opt = None

    if request.method == "POST":
        session["option"] = opt = request.form.get("sub")
        return redirect(url_for("messagefun", option=opt))
    return render_template("check.html", name=name_, opinion="awesome guy", description=description_,
                           reason="good", connection="yes", irritating="no", improvements=improvements_)

@app.route("/message", methods=["POST", "GET"])
def messagefun():
    name = session.get("name")
    opt = session.get("option")
    return render_template("message.html", name=name, option=opt)

@app.route('/show_data')
def show_data():
    conn = sqlite3.connect(PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM response")
    data = cursor.fetchall()
    conn.close()
    return render_template('show_data.html', data=data)

if __name__ == "__main__":
    db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
