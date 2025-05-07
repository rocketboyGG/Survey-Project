from flask import Flask, render_template
from sqlite3 import Connection

app = Flask(__name__)

def addResultsToDatabase(name, age):
    try:
        con = Connection("SurveyDatabase.db")
        cur = con.cursor()
        params = (name, age)
        sql = """INSERT INTO Survey1 (name, age) VALUES(?, ?)"""
        cur.execute(sql, params)
        cur.commit()
        con.close()
    except:
        print("Failed to connect to database!")

@app.route("/")
def home():
    addResultsToDatabase("Theo", 26)
    return render_template("home.html")

@app.route("/Spørgeskema1/")
def spørgeskema1():
    return render_template("Spørgeskema1.html")

@app.route("/Login/")
def login():
    return render_template("Login.html")

if __name__ == ('__main__'):
    app.run(host="0.0.0.0", debug=True)
