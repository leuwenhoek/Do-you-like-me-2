from flask import Flask, request, redirect, render_template, url_for, session
import sqlite3
import datetime
import os

app = Flask(__name__)
PATH = os.path.join(os.path.dirname(__file__), "database.db")
app.secret_key = "very-very-secret"

def db():
    print(f"Creating database at: {PATH}")
    conn = sqlite3.connect(PATH)
    curr = conn.cursor()
    curr.execute('''
        CREATE TABLE IF NOT EXISTS response (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            opinion TEXT NOT NULL,
            description TEXT NOT NULL,
            reason TEXT NOT NULL,
            connection TEXT NOT NULL,
            irritating TEXT NOT NULL,
            improvements TEXT NOT NULL,
            date DATE DEFAULT CURRENT_DATE,
            time TIME DEFAULT CURRENT_TIME
        )
    ''')
    conn.commit()
    conn.close()

with app.app_context():
    db()

@app.route("/", methods=["POST", "GET"])
def main():
    return redirect(url_for("formfun"))

@app.route("/form", methods=["POST", "GET"])
def formfun():
    if request.method == "POST":
        try:
            session["name"] = name = request.form.get("name")
            session["opinion"] = opinion = request.form.get("opinion")
            session["description"] = description = request.form.get("description")
            session["reason"] = reason = request.form.get("reason")
            session["connection"] = connection = request.form.get("connection")
            session["irritating"] = irritating = request.form.get("irritating")
            session["improvements"] = improvements = request.form.get("improvements")
            current_time = datetime.datetime.now()
            conn = sqlite3.connect(PATH)
            curr = conn.cursor()
            curr.execute('''
                INSERT INTO response
                (name, opinion, description, reason, connection, irritating, improvements, time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, opinion, description, reason, connection, irritating, improvements, current_time))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return "An error occurred while saving data", 500
        finally:
            conn.close()
        return redirect(url_for("checkfun"))
    return render_template("index.html")

@app.route("/check", methods=["POST", "GET"])
def checkfun():
    name_ = session.get("name", "Unknown")
    description_ = session.get("description", "")
    improvements_ = session.get("improvements", "")
    opt = None
    if request.method == "POST":
        session["option"] = opt = request.form.get("sub")
        return redirect(url_for("messagefun", option=opt))
    return render_template("check.html", name=name_, opinion="awesome guy", description=description_, reason="good", connection="yes", irritating="no", improvements=improvements_)

@app.route("/message", methods=["POST", "GET"])
def messagefun():
    name = session.get("name", "Unknown")
    opt = session.get("option")
    return render_template("message.html", name=name, option=opt)

@app.route('/show_data')
def show_data():
    try:
        conn = sqlite3.connect(PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM response")
        data = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return "An error occurred while fetching data", 500
    finally:
        conn.close()
    return render_template('show_data.html', data=data)