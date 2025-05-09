from flask import Flask, request, render_template, redirect, url_for 
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///SurveyDatabase.db"
app.secret_key = b"c14b9c56bfdf5e2c323ef19e9d6fa73612c5bac72b79fbfaa89c17f30c975fb4"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = Users.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("patientList"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/spørgeskema1/")
def sporgeskema1():
    return render_template("spørgeskema1.html")

@app.route("/patientList/")
@login_required
def patientList():
    return render_template("patientList.html", username=current_user.username)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__ == ('__main__'):
    app.run(host="0.0.0.0", debug=True)
