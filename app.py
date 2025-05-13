from flask import Flask, request, render_template, redirect, url_for 
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
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
    patient = db.relationship('Patient', backref='responses', lazy=True)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questionid = db.Column(db.Integer,db.ForeignKey('question.id'), nullable=False)
    choiceid = db.Column(db.Integer,db.ForeignKey('choice.id'), nullable=False)
    responseid = db.Column(db.Integer,db.ForeignKey('response.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    question = db.relationship('Question', backref='answers', lazy=True)
    choice = db.relationship('Choice', backref='answers', lazy=True)

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
            return redirect(url_for("patientlist"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/")
def home():
    #create_survey_1()
    #generate_admin_login()
    return render_template("home.html")

@app.route("/patientlist/")
@login_required
def patientlist():
    patients = Patient.query.all()
    return render_template("patientlist.html", username=current_user.username, patients=patients)

@app.route("/go_to_patient/<int:patientid>")
@login_required
def go_to_patient(patientid):
    return redirect(url_for("patientdata", patientid=patientid))

@app.route("/patientdata/<int:patientid>")
@login_required
def patientdata(patientid):
    responses = Response.query.filter_by(patientid=patientid).all()
    return render_template("patientdata.html", responses=responses)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/survey", methods = ["GET", "POST"])
def survey():
    survey = Survey.query.get_or_404(1)
    if request.method == "POST":
        patient = Patient(
            firstname=request.form["firstname"], 
            lastname=request.form["lastname"],
            cpr=request.form["cpr"])
        db.session.add(patient)
        db.session.flush()
        response = Response(surveyid=survey.id, patientid=patient.id)
        db.session.add(response)
        db.session.flush()

        for question in survey.questions:
            fieldOption = f"question_{question.id}"
            fieldText = f"question_{question.id}_uddyb"
            value = request.form.get(fieldOption)
            text = request.form.get(fieldText)

            answer = Answer(questionid=question.id,choiceid=int(value), responseid=response.id, text=text)
            db.session.add(answer)

        db.session.commit()
            
    return render_template("survey.html", survey=survey)

def create_survey_1():
    survey = Survey(title="Spørgeskema1", desc="Spørgeskema om søvnvaner")
    db.session.add(survey)
    db.session.flush()
    q1 = Question(
        surveyid=survey.id,
        text="Sover du alene?"
    )
    db.session.add(q1)
    db.session.flush()
    q1ch1 = Choice(
        questionid=q1.id,
        text="Ja"
    )
    q1ch2 = Choice(
        questionid=q1.id,
        text="Nej"
    )
    db.session.add_all([q1ch1, q1ch2])

    q2 = Question(
        surveyid=survey.id,
        text="Føler du dig veludhvilet, når du vågner?"
    )
    db.session.add(q2)
    db.session.flush()
    q2ch1 = Choice(
        questionid=q2.id,
        text="Ja"
    )
    q2ch2 = Choice(
        questionid=q2.id,
        text="Nej"
    )
    db.session.add_all([q2ch1, q2ch2])

    q3 = Question(
        surveyid=survey.id,
        text="Har du oplevet søvnparalyse?"
    )
    db.session.add(q3)
    db.session.flush()
    q3ch1 = Choice(
        questionid=q3.id,
        text="Ja"
    )
    q3ch2 = Choice(
        questionid=q3.id,
        text="Nej"
    )
    db.session.add_all([q3ch1, q3ch2])

    q4 = Question(
        surveyid=survey.id,
        text="Hvad laver du, fra du ligger dig i sengen, til du sover?"
    )
    db.session.add(q4)
    db.session.flush()
    q4ch1 = Choice(
        questionid=q4.id,
        text="Ligger med din telefon"
    )
    q4ch2 = Choice(
        questionid=q4.id,
        text="Læser en bog"
    )
    q4ch3 = Choice(
        questionid=q4.id,
        text="Mediterer"
    )
    q4ch4 = Choice(
        questionid=q4.id,
        text="Onanerer"
    )
    q4ch5 = Choice(
        questionid=q4.id,
        text="Har sex"
    )
    q4ch6 = Choice(
        questionid=q4.id,
        text="Ser TV"
    )
    q4ch7 = Choice(
        questionid=q4.id,
        text="Tænker meget over ting"
    )
    db.session.add_all([q4ch1, q4ch2, q4ch3, q4ch4, q4ch5, q4ch6, q4ch7])
    db.session.commit()

def generate_admin_login():
    password = "123"
    hashpass = generate_password_hash(password)
    admin = Users(username="admin", password=hashpass)
    db.session.add(admin)
    db.session.commit()

if __name__ == ('__main__'):
    app.run(host="0.0.0.0", debug=True)
