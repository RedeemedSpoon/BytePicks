from flask import Flask, render_template
from datetime import datetime
from youtube import AllVideos

app = Flask("__main__")
copyright_year = datetime.now().year


@app.route("/")
def home():
    return render_template("home.html", year=copyright_year, videos=AllVideos)


@app.route("/Dashboard")
def dashboard():
    return render_template("dashboard.html", year=copyright_year, videos=AllVideos)


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


def formatViewCount(number):
    if number / 1_000 > 1:
        return str(round(number / 1_000, 1)) + "K"
    elif number / 1_000_000 > 1:
        return str(round(number / 1_000_000, 1)) + "M"
    elif number > 1_000_000_000:
        return str(round(number / 1_000_000_000, 1)) + "B"
    else:
        return str(number)


def formatDuration(duration):
    hours, minutes, seconds = map(int, duration.split(":"))
    if hours == 0 and minutes < 10:
        return f"{minutes}:{seconds:02d}"
    elif hours == 0:
        return f"{minutes:02d}:{seconds:02d}"
    else:
        return duration


if __name__ == "__main__":
    app.jinja_env.globals.update(formatViewCount=formatViewCount, formatDuration=formatDuration)
    app.run(debug=True)
