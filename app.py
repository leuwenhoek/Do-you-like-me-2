from flask import Flask, request, redirect, render_template, url_for, session
import sqlite3
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
PATH = os.path.join(os.path.dirname(__file__), "database.db")
app.secret_key = "very-very-secret"

# Email configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # Set in .env file (e.g., your_actual_email@gmail.com)
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Set in .env file (e.g., your App Password)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

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
            date DATE DEFAULT CURRENT_DATE,
            time TIME DEFAULT CURRENT_TIME
        )
    ''')
    conn.commit()
    conn.close()

def send_email(data):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS  # Sending to yourself; change if needed
    msg['Subject'] = 'New Form Submission'

    body = f"""
    New form submission received at {data['time']} on {data['date']} (IST):
    
    Name: {data['name']}
    Opinion: {data['opinion']}
    Description: {data['description']}
    Reason: {data['reason']}
    Connection: {data['connection']}
    Irritating: {data['irritating']}
    Improvements: {data['improvements']}
    Date: {data['date']}
    Time: {data['time']}
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

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

        # Get current time in IST
        ist_offset = datetime.timedelta(hours=5, minutes=30)  # IST is UTC+5:30
        current_time = datetime.datetime.now(datetime.timezone.utc) + ist_offset
        current_date = current_time.strftime("%Y-%m-%d")
        time_str = current_time.strftime("%H:%M:%S")

        # Insert data into the database
        conn = sqlite3.connect(PATH)
        curr = conn.cursor()
        curr.execute('''
            INSERT INTO response
            (name, opinion, description, reason, connection, irritating, improvements, date, time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, opinion, description, reason, connection, irritating, improvements, current_date, time_str))
        conn.commit()
        conn.close()

        # Prepare data for email
        email_data = {
            'name': name,
            'opinion': opinion,
            'description': description,
            'reason': reason,
            'connection': connection,
            'irritating': irritating,
            'improvements': improvements,
            'date': current_date,
            'time': time_str
        }
        send_email(email_data)
        return redirect(url_for("checkfun"))
    return render_template("index.html")

@app.route("/check", methods=["POST", "GET"])
def checkfun():
    name_ = session.get("name")
    description_ = session["description"]
    improvements_ = session["improvements"]
    opt = None
    if request.method == "POST":
        session["option"] = opt = request.form.get("sub")
        return redirect(url_for("messagefun", option=opt))
    return render_template("check.html", name=name_, opinion="awesome guy", description=description_, reason="good", connection="yes", irritating="no", improvements=improvements_)

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
    port = int(os.getenv("PORT", 5000))  # Use Render's PORT or 5000 locally
    db()
    app.run(host="0.0.0.0", port=port, debug=True)