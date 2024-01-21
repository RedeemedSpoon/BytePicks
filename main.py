from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json

TIME = ["daily", "weeky", "monthy", "yearly"]
LANGUAGE = ["EN", "FR", "ES", "DE", "PT", "RU", "HI"]
app = Flask("__main__")
copyright_year = datetime.now().year
with open("videos/daily.json", "r") as file:
    AllVideos = json.load(file)


@app.route("/")
def home():
    return render_template("home.html", year=copyright_year, videos=AllVideos)


@app.route("/Dashboard")
def dashboard():
    time = request.args.get("time", default="daily")
    language = request.args.get("lang", default="EN")
    specificVideos = getVideos(time, language)
    return render_template("dashboard.html", year=copyright_year, videos=specificVideos, time=time, language=language)


@app.route("/api/request")
def apiRequest():
    time = request.args.get("time", default="daily")
    language = request.args.get("lang", default="EN")
    top = request.args.get("top", default=25, type=int)

    if time in TIME and language in LANGUAGE and top > 0:
        requestedVideos = list(getVideos(time, language).values())[:top]
        response = {
            "Request": f"The top {top} {time} videos in {language}",
            "Date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Result": requestedVideos,
        }

    else:
        response = {"Result": "You gave an invalid request."}

    return jsonify(response)


@app.route("/Api-Docs")
def api():
    return render_template("api.html", year=copyright_year)


@app.route("/Email")
def email():
    return render_template("email.html", year=copyright_year)


@app.route("/Messages")
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


def getVideos(time, language):
    with open(f"videos/{time}.json", "r") as file:
        timeVideos = json.load(file)

    langSpecificVideos = {key: value for key, value in timeVideos.items() if value["language"] == language}
    return langSpecificVideos


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
