from flask import Flask, request, render_template, redirect, url_for 
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from datetime import datetime

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

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    cpr = db.Column(db.String(12), nullable=False)

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    desc = db.Column(db.Text)
    questions = db.relationship('Question', backref='survey', cascade="all, delete-orphan")
    responses = db.relationship('Response', backref='survey', cascade="all, delete-orphan")

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surveyid = db.Column(db.Integer,db.ForeignKey('survey.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    choices = db.relationship('Choice', backref='question', cascade="all, delete-orphan")

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questionid = db.Column(db.Integer,db.ForeignKey('question.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surveyid = db.Column(db.Integer,db.ForeignKey('survey.id'), nullable=False)
    patientid = db.Column(db.Integer,db.ForeignKey('patient.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now()) 
    answers = db.relationship('Answer', backref='response', cascade="all, delete-orphan")

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questionid = db.Column(db.Integer,db.ForeignKey('question.id'), nullable=False)
    choiceid = db.Column(db.Integer,db.ForeignKey('choice.id'), nullable=False)
    responseid = db.Column(db.Integer,db.ForeignKey('response.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)

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

@app.route("/spørgeskema1/", methods = ["GET", "POST"])
def spørgeskema1():
    if request.method == "POST":
        patient = Patient(firstname=request.form["fornavn"], 
                          lastname=request.form["efternavn"],
                          cpr=request.form["cpr"])

        db.session.add(patient)
        db.session.flush()
        survey = Survey.query.filter_by(title="Spørgeskema1").first()
        if survey is None:
            survey = Survey(title="Spørgeskema1", desc="Spørgeskema om søvnvaner")
            db.session.add(survey)
            db.session.flush()

        response = Response(
            surveyid = survey.id,
            patientid = patient.id
        )
        db.session.add(response)
        db.session.flush()

        """ Add question 1"""
        sp1tekst = request.form["sp1tekst"] 
        q1 = Question.query.filter_by(text=sp1tekst).first()
        if q1 is None:
            q1 = Question(
                surveyid=survey.id, 
                text=sp1tekst
            )
            db.session.add(q1)
            db.session.flush()
            q1ch1 = Choice(
                questionid = q1.id,
                text = request.form["sp1option1"]
            )
            q1ch2 = Choice(
                questionid = q1.id,
                text = request.form["sp1option2"]
            )
            db.session.add(q1ch1)
            db.session.add(q1ch2)
            db.session.commit()

        q1svar = Choice.query.filter_by(text=request.form["sp1svar"], questionid=q1.id).first()
        q1ans = Answer(
            questionid = q1.id,
            choiceid =  q1svar.id,
            responseid = response.id,
            text = request.form["sp1uddyb"]
        )
        db.session.add(q1ans)

        """ Add question 2"""
        sp2tekst = request.form["sp2tekst"] 
        q2 = Question.query.filter_by(text=sp2tekst).first()
        if q2 is None:
            q2 = Question(
                surveyid=survey.id, 
                text=request.form["sp2tekst"]
            )
            db.session.add(q2)
            db.session.flush()
            q2ch1 = Choice(
                questionid = q2.id,
                text = request.form["sp2option1"]
            )
            q2ch2 = Choice(
                questionid = q2.id,
                text = request.form["sp2option2"]
            )
            db.session.add(q2ch1)
            db.session.add(q2ch2)
            db.session.commit()

        q2svar = Choice.query.filter_by(text=request.form["sp2svar"], questionid=q2.id).first()
        q2ans = Answer(
            questionid = q2.id,
            choiceid =  q2svar.id,
            responseid = response.id,
            text = request.form["sp2uddyb"]
        )
        db.session.add(q2ans)

        """ Add question 3"""
        sp3tekst = request.form["sp3tekst"] 
        q3 = Question.query.filter_by(text=sp3tekst).first()
        if q3 is None:
            q3 = Question(
                surveyid=survey.id, 
                text=request.form["sp3tekst"]
            )
            db.session.add(q3)
            db.session.flush()
            q3ch1 = Choice(
                questionid = q3.id,
                text = request.form["sp3option1"]
            )
            q3ch2 = Choice(
                questionid = q3.id,
                text = request.form["sp3option2"]
            )
            db.session.add(q3ch1)
            db.session.add(q3ch2)
            db.session.commit()

        q3svar = Choice.query.filter_by(text=request.form["sp3svar"], questionid=q3.id).first()
        q3ans = Answer(
            questionid = q3.id,
            choiceid =  q3svar.id,
            responseid = response.id,
            text = request.form["sp3uddyb"]
        )
        db.session.add(q3ans)

        """ Add question 4"""
        sp4tekst = request.form["sp4tekst"] 
        q4 = Question.query.filter_by(text=sp4tekst).first()
        if q4 is None:
            q4 = Question(
                surveyid=survey.id, 
                text=request.form["sp4tekst"]
            )
            db.session.add(q4)
            db.session.flush()
            q4ch1 = Choice(
                questionid = q4.id,
                text = request.form["sp4option1"]
            )
            q4ch2 = Choice(
                questionid = q4.id,
                text = request.form["sp4option2"]
            )
            q4ch3 = Choice(
                questionid = q4.id,
                text = request.form["sp4option3"]
            )
            q4ch4 = Choice(
                questionid = q4.id,
                text = request.form["sp4option4"]
            )
            q4ch5 = Choice(
                questionid = q4.id,
                text = request.form["sp4option5"]
            )
            q4ch6 = Choice(
                questionid = q4.id,
                text = request.form["sp4option6"]
            )
            q4ch7 = Choice(
                questionid = q4.id,
                text = request.form["sp4option7"]
            )
            db.session.add(q4ch1)
            db.session.add(q4ch2)
            db.session.add(q4ch3)
            db.session.add(q4ch4)
            db.session.add(q4ch5)
            db.session.add(q4ch6)
            db.session.add(q4ch7)
            db.session.commit()

        q4svar = Choice.query.filter_by(text=request.form["sp4svar"], questionid=q4.id).first()
        q4ans = Answer(
            questionid = q4.id,
            choiceid =  q4svar.id,
            responseid = response.id,
            text = request.form["sp4uddyb"]
        )
        db.session.add(q4ans)
        db.session.commit()
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
