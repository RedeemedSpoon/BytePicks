from flask import Flask, render_template, jsonify, request
from datetime import datetime
import json, secrets, string
from common import *

TIME = ["daily", "weeky", "monthy", "yearly"]
LANGUAGE = ["EN", "FR", "ES", "DE", "PT", "RU", "HI"]
app = Flask("__main__")
copyright_year = datetime.now().year


@app.teardown_request
def teardown_request(exception=None):
    session.close()


@app.route("/")
def home():
    with open("videos/daily.json", "r") as file:
        homeThumbnails = json.load(file)
    return render_template("home.html", year=copyright_year, videos=homeThumbnails)


@app.route("/Dashboard")
def dashboard():
    time = request.args.get("time", default="daily")
    language = request.args.get("lang", default="EN")
    specificVideos = getVideos(time, language)
    return render_template("dashboard.html", year=copyright_year, videos=specificVideos, time=time, language=language)


@app.route("/Api-Docs")
def api():
    return render_template("api.html", year=copyright_year)


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


@app.route("/Newsletter", methods=["GET", "POST"])
def newsletter():
    message = None
    if request.method == "POST":
        email = request.form["user_email"]
        time = request.form["time"]
        language = request.form["language"]
        token = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))

        user = session.query(User).filter_by(email=email).first()
        if user:
            user.time, user.language, user.token, message = time, language, token, "User info updated!"
        else:
            session.add(User(email=email, time=time, language=language, token=token))
            message = "Thank you for subscribing!"
        session.commit()

    return render_template("newsletter.html", year=copyright_year, message=message)


@app.route("/drop/user")
def drop():
    token = request.args.get("token", default=None)
    if token is None:
        return render_template("newsletter.html", year=copyright_year, message="Missing token")

    user = session.query(User).filter_by(token=token).first()
    if user:
        session.delete(user)
        session.commit()
        return render_template("newsletter.html", year=copyright_year, message="User deleted")
    else:
        return render_template("newsletter.html", year=copyright_year, message="User not found")


@app.route("/Explaination")
def explaination():
    return render_template("explaination.html", year=copyright_year)


@app.route("/Privacy-Policy")
def privacy_policy():
    return render_template("privacy-policy.html", year=copyright_year)


@app.route("/About-Us")
def about_us():
    return render_template("about-us.html", year=copyright_year)


@app.route("/Contact", methods=["GET", "POST"])
def contact():
    message = None
    if request.method == "POST":
        initializeEmail()
        sender = "Anonymous Person" if request.form["name"] == "" else request.form["email"]
        email = f"Subject: {request.form['subject']}\n\n{request.form['message']}\nThis message was sent by : {sender}"
        server.sendmail(senderEmail, senderPassword, email)
        server.close()
        message = "Thank you for contacting us!"

    return render_template("contact.html", year=copyright_year, message=message)


if __name__ == "__main__":
    app.jinja_env.globals.update(formatViewCount=formatViewCount, formatDuration=formatDuration)
    app.run()
