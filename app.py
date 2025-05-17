from flask import Flask, request, render_template, redirect, url_for 
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from uuid import uuid4
import matplotlib.pyplot as plt
import io
import base64

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
    uuid = db.Column(db.String(36), nullable=False)
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
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/")
def home():
    #create_survey_1()
    #generate_admin_login()
    return render_template("home.html")

@app.route("/admin_dashboard/")
@login_required
def admin_dashboard():
    patients = Patient.query.all()
    return render_template("admin_dashboard.html", username=current_user.username, patients=patients)

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

@app.route("/survey/<string:param>", methods = ["GET", "POST"])
def survey(param):
    survey = Survey.query.filter_by(uuid=param).first()
    if request.method == "POST":
        patient = Patient.query.filter_by(cpr=request.form["cpr"]).first()
        if patient is None:
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
            
    return render_template("survey.html", survey=survey, param=param)

#Route til survey builder
@app.route('/survey_builder', methods=['GET', 'POST'])  #GET viser HTML-siden, når man besøger siden(GET request), POST er når man submitter dataen til databasen
@login_required #Kræver login for at access
def survey_builder():   #Survey builder funktion
    if request.method == "POST":    #Sker kun på en POST request(submit knap)
        title = request.form.get('title')   #Tager den string som er indtastet i det html tekst input som har: name="title"
        description = request.form.get('description')   #Tager den string som er indtastet i det html tekst input som har: name="description"
        questions_data = request.form.getlist('questions')  #Tager alle inputs som har: name="questions" og gemmer dem som en liste

        if not title or not questions_data: #Sørger for at man ikke kan submit et survey uden minimum titel og et spørgsmål, men eftersom vores tekst input er sat som required,
            return "Missing data", 400      # er det her kun som ekstra sikkerhed på backend. Fordi det er muligt at bypass required client-side
                                            #400 = HTTP status code:"Bad Request"
        #Laver nyt survey
        new_survey = Survey(uuid=str(uuid4()), title=title, desc=description)  #Laver et new_survey objekt fra Survey class'en og vælger hvilke værdier der skal indsættes på title og desc
        db.session.add(new_survey)  #Tilføjer new_survey til SQLAlchemy sessionen
        db.session.flush()  #Pusher til databasen uden at commit, for at få et ID for survey(skal bruges til questions)

        #Loop igennem questions og tilhørende choices
        for i, question_text in enumerate(questions_data):  #enumerate tilknytter et index(i) tal, til hver question string, for bedre at holde styr på det
            
            #Laver nyt question
            question = Question(text=question_text, surveyid=new_survey.id) #Laver et question objekt fra Question class'en og vælger hvilke værdier der skal indsættes på text og surveyid
            db.session.add(question)    #Tilføjer question til SQLAlchemy sessionen
            db.session.flush()  #Pusher til databasen uden at commit, for at få et ID for question (skal brues til choices)

            #Henter choices for dette spørgsmål
            choices_name = f'choices_{i}[]' #Tildeler alle choices samme index(i) tal som spørgsmålet de tilhører
            question_choices = request.form.getlist(choices_name)   #Tager alle inputs som har: name="choices_{i}[]" og gemmer dem som en liste

            #Tilføjer choices til databasen
            for choice_text in question_choices:    #Looper igennem alle choices og tilføjer dem en ad gangen
                if choice_text.strip():  #Sikre at de ikke er tomme. Endnu et backend sikkerheds check eftersom tekst input er sat som required.
                    choice = Choice(text=choice_text, questionid=question.id)   #Laver et question objekt fra Question class'en og vælger hvilke værdier der skal indsættes på text og questionid
                    db.session.add(choice)  #Tilføjer choice til SQLAlchemy sessionen

        db.session.commit()     #Commit'er til databasen
        return redirect(url_for('admin_dashboard'))    #Sender tilbage til homepage efter spørgeskema tilføjes til database

    return render_template('survey_builder.html')   #Loader HTML-siden, koden kommer med det samme her ned eftersom at survey_builder funktionen først bliver kørt igennem ved at trykke på submit knappen(POST request)


@app.route("/survey_list")
@login_required
def survey_list():
    surveys = Survey.query.all()
    return render_template('survey_list.html', surveys=surveys)

@app.route("/survey_stats/<string:param>")
@login_required
def survey_stats(param):
    survey = Survey.query.filter_by(uuid=param).first()
    plots = []
    if len(survey.responses) != 0:
        for question in survey.questions:
            labels = []
            data = []
            for choice in question.choices:
                labels.append(choice.text)
                data.append(len(choice.answers))
            print(labels, data)
            fig, ax = plt.subplots()
            ax.pie(data, labels=labels, autopct='%1.1f%%')
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            img_base64 = base64.b64encode(img.getvalue()).decode()
            plots.append((question, img_base64))
             
    return render_template("survey_stats.html", plots=plots, number_of_res=len(survey.responses))

@app.route("/deletesurvey/<string:param>")
@login_required
def deletesurvey(param):
    survey = Survey.query.filter_by(uuid=param).first()
    with db.session.no_autoflush:
        for response in survey.responses:
            patient = response.patient
            number_of_same_surveys = 0
            for res in patient.responses:
                if res.surveyid == survey.id:
                    number_of_same_surveys += 1
            if number_of_same_surveys == len(patient.responses):
                db.session.delete(patient)
        db.session.delete(survey)
    db.session.commit()
    return redirect(url_for("survey_list"))

def create_survey_1():
    survey = Survey(uuid=str(uuid4()), title="Spørgeskema1", desc="Spørgeskema om søvnvaner")
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
