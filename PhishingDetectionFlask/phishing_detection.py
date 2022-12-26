from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/team")
def team():
    return render_template("team.html")

if __name__ == '__main__':
    app.run(debug=True)