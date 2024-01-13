from flask import Flask, render_template, request
from datetime import datetime

app = Flask("__main__")
copyright_year = datetime.now().year


@app.route("/")
def home():
    return render_template("home.html", year=copyright_year)


@app.route("/Dashboard")
def dashboard():
    return render_template("api.html", year=copyright_year)


@app.route("/Api")
def api():
    return render_template("api.html", year=copyright_year)


@app.route("/Email")
def email():
    return render_template("email.html", year=copyright_year)


@app.route("/SMS")
def sms():
    return render_template("sms.html", year=copyright_year)


@app.route("/Explaination")
def explaination():
    return render_template("explaination.html", year=copyright_year)


@app.route("/Success")
def success():
    return render_template("success.html", year=copyright_year)


@app.route("/Privacy-Policy")
def privacy_policy():
    return render_template("privacy-policy.html", year=copyright_year)


@app.route("/About-Me")
def about_me():
    return render_template("about-me.html", year=copyright_year)


@app.route("/Contact")
def contact():
    return render_template("contact.html", year=copyright_year)


def submit():
    if request.method == "POST":
        return render_template("success.html", year=copyright_year)


if __name__ == "__main__":
    app.run(debug=True)
