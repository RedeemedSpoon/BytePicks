from flask import Flask, render_template, request
from datetime import datetime
import json

app = Flask("__main__")
copyright_year = datetime.now().year
with open("./videos/daily.json") as file:
    allVideos = json.load(file)


@app.route("/")
def home():
    return render_template("home.html", year=copyright_year, videos=allVideos)


@app.route("/Dashboard")
def dashboard():
    return render_template("dashboard.html", year=copyright_year, videos=allVideos)


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


@app.route("/Privacy-Policy")
def privacy_policy():
    return render_template("privacy-policy.html", year=copyright_year)


@app.route("/About-Us")
def about_us():
    return render_template("about-us.html", year=copyright_year)


@app.route("/Contact")
def contact():
    return render_template("contact.html", year=copyright_year)


if __name__ == "__main__":
    app.run(debug=True)
