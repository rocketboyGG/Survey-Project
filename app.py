from flask import Flask, request,  render_template
from sqlite3 import Connection

app = Flask(__name__)

def addResultsToDatabase(name, age):
    try:
        con = Connection("SurveyDatabase.db")
        cur = con.cursor()
        params = (name, age)
        sql = """INSERT INTO Survey1 (name, age) VALUES(?, ?)"""
        cur.execute(sql, params)
        con.commit()
        con.close()
    except:
        print("Failed to connect to database!")

@app.route("/")
def home():
    #addResultsToDatabase("Theo", 26)
    return render_template("home.html")

@app.route("/Spørgeskema1/")
def spørgeskema1():
    return render_template("Spørgeskema1.html")

@app.route("/login/")
def login():
    return render_template("login.html")


@app.route("/testInsertDatabase/", methods = ["GET", "POST"])
def testInsertDatabase():
    if request.method == "POST":
        name = request.form.get("fname")
        age =  request.form.get("age")
        addResultsToDatabase(name, age)
    return render_template("testInsertDatabase.html")

if __name__ == ('__main__'):
    app.run(host="0.0.0.0", debug=True)
