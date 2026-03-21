# BeehiveOfAI - Website for the Beehive Of AI distributed computing platform

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/hives")
def hives():
    return render_template("hives.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
