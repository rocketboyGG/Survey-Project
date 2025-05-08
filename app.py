from flask import Flask, request, render_template, redirect, url_for, render_template_string
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin
from sqlite3 import Connection


app = Flask(__name__)
app.secret_key = b"c14b9c56bfdf5e2c323ef19e9d6fa73612c5bac72b79fbfaa89c17f30c975fb4"
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.password = password

users = {'elias': User('elias', 'secret')}

@login_manager.user_loader
def user_loader(id):
    return users.get(id)

@app.route("/login/", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        user = users.get(request.form.get("username"))

        if user is None or user.password != request.form["password"]:
            print("FAILED")
            return redirect(url_for("login"))

        print("YAAAAA!")
        login_user(user)
        return redirect(url_for("protected"))
    else:
        return render_template("Login.html")

@app.route("/protected")
@login_required
def protected():
    return render_template_string(
        "Logged in as: {{ user.id }}",
        user=current_user
    )

@app.route("/logout")
def logout():
    logout_user()
    return "Logged out"

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

@app.route("/testInsertDatabase/", methods = ["GET", "POST"])
def testInsertDatabase():
    if request.method == "POST":
        name = request.form.get("fname")
        age =  request.form.get("age")
        addResultsToDatabase(name, age)
    return render_template("testInsertDatabase.html")

if __name__ == ('__main__'):
    app.run(host="0.0.0.0", debug=True)
