from flask import Flask, render_template
#from flask_login import LoginManager
from sqlite3 import Connection

#login_manager = LoginManager()

app = Flask(__name__)
#login_manager.init_app(app)
app.secret_key = b"c14b9c56bfdf5e2c323ef19e9d6fa73612c5bac72b79fbfaa89c17f30c975fb4"
"""
def addResultsToDatabase(name, age):
    try:
        con = Connection("SurveyDatabase.db")
        cur = con.cursor()
        params = (name, age)
        sql = INSERT INTO Survey1 (name, age) VALUES(?, ?)
        cur.execute(sql, params)
        cur.commit()
        con.close()
    except:
        print("Failed to connect to database!")

users = {'Elias': {'password': '1234deez'}}

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(user)

        flask.flash('Logged in successfully.')

        next = flask.request.args.get('next')
        # url_has_allowed_host_and_scheme should check if the url is safe
        # for redirects, meaning it matches the request host.
        # See Django's url_has_allowed_host_and_scheme for an example.
        if not url_has_allowed_host_and_scheme(next, request.host):
            return flask.abort(400)

        return flask.redirect(next or flask.url_for('index'))
    return flask.render_template('login.html', form=form)
"""
@app.route("/")
def home():
    #addResultsToDatabase("Theo", 26)
    return render_template("home.html")

@app.route("/Spørgeskema1/")
def spørgeskema1():
    return render_template("Spørgeskema1.html")

@app.route("/test/")
def test():
    return render_template("test.html")

@app.route("/login/")
def login():
    return render_template("login.html")

if __name__ == ('__main__'):
    app.run(host="0.0.0.0", debug=True)
