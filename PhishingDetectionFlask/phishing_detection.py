from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    con = sqlite3.connect("websites.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM WEBSITE")
    rows = cur.fetchall()
    return render_template("home.html", rows=rows)

@app.route("/team")
def team():
    return render_template("team.html")

if __name__ == '__main__':
    app.run(debug=True)