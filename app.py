from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/site1/")
def site1():
    return render_template("site1.html")

@app.route("/site2/")
def site2():
    return render_template("site2.html")

if __name__ == ('__main__'):
    app.run(host="0.0.0.0", debug=True)
