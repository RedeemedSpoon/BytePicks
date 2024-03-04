from flask import Flask, render_template, jsonify, request, send_file
from collections import OrderedDict
from datetime import datetime
import json, secrets, string
from common import *

TIME = ["daily", "weeky", "monthy", "yearly"]
LANGUAGE = ["EN", "FR", "ES", "RU", "HI"]
app = Flask(__name__)
copyrightYear = datetime.now().year

@app.teardown_request
def teardown_request(exception=None):
    session.close()

@app.route("/")
def home():
    with open("daily.json", "r") as file:
        homeThumbnails = json.load(file)["EN"]
    return render_template("home.html", year=copyrightYear, videos=homeThumbnails)

@app.route("/Dashboard")
def dashboard():
    time = request.args.get("time", default="daily")
    language = request.args.get("lang", default="EN")
    specificVideos = getVideos(time, language)
    return render_template("dashboard.html", year=copyrightYear,
        videos=specificVideos, time=time,language=language,
        formatDuration=formatDuration, formatViewCount=formatViewCount,
    )

@app.route("/Api-Docs")
def api():
    return render_template("api.html", year=copyrightYear)

@app.route("/api/request")
def apiRequest():
    time = request.args.get("time", default="daily")
    language = request.args.get("lang", default="EN")
    top = request.args.get("top", default=25, type=int)

    if time in TIME and language in LANGUAGE and top > 0:
        response = {
            "Request": f"The top {top} {time} videos in {language}",
            "Date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Result": OrderedDict(list(getVideos(time, language).items())[:top]),
        }
    else:
        response = {"Result": "You send an invalid request."}

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
            message = "This Email is Already Registered"
        else:
            user = session.query(PendingUser).filter_by(email=email).first()
            if user:
                message = "This User is on the Pending List"
            else:
                session.add(PendingUser(email=email, time=time, language=language, token=token))
                session.commit()

                message = getMessage(email, time, language, token)
                sendEmail(message, "BytePicks : Please Confirm Your Email", email, "newsletter@bytepicks.com")
                message = "Please Check Your Inbox!"

    return render_template("newsletter.html", year=copyrightYear, message=message, email="")

@app.route("/Submit", methods=["GET", "POST"])
def submit():
    token = request.args.get("token", default=None)
    email = request.args.get("user", default="")
    message = None
    if token is None or email == "":
        message = "Missing Token or Email"
    else:
        user = session.query(User).filter_by(token=token, email=email).first()
        if user:
            message = "User Already Exists"
        else:
            user = session.query(PendingUser).filter_by(email=email).first()
            if user:
                session.add(User(email=user.email, time=user.time, language=user.language, token=user.token))
                session.delete(user)
                session.commit()
                message = "Thank You for Subscribing!"
            else:
                message = "This User Does not Exist"

    return render_template("newsletter.html", year=copyrightYear, message=message, email="")

@app.route("/Edit", methods=["GET", "POST"])
def edit():
    token = request.args.get("token", default=None)
    email = request.args.get("user", default="")
    message = None
    if request.method == "POST":
        if token is None or email == "":
            message = "Missing Token or Email"
        else:
            user = session.query(User).filter_by(token=token, email=email).first()
            if user:
                user.time = request.form["time"]
                user.language = request.form["language"]
                message = "User Preference Updated!"
            else:
                message = "Incorrect Token or Email"
    
    return render_template("newsletter.html", year=copyrightYear, message=message, email=email)

@app.route("/Drop", methods=["GET", "POST"])
def drop():
    token = request.args.get("token", default=None)
    email = request.args.get("user", default="")
    if token is None or email == "":
        message = "Missing Token or Email"
    else:
        user = session.query(User).filter_by(token=token, email=email).first()
        if user:
            session.delete(user)
            session.commit()
            message = "User Deleted!"
        else:
            message = "Incorrect Token or Email"
    return render_template("newsletter.html", year=copyrightYear, message=message, email="")

@app.route("/Download")
def download():
	return send_file("channels.csv", as_attachment=True)

@app.route("/Explaination")
def explaination():
    return render_template("explaination.html", year=copyrightYear)

@app.route("/Privacy-Policy")
def privacy_policy():
    return render_template("privacy-policy.html", year=copyrightYear)

@app.route("/About-Us")
def about_us():
    return render_template("about-us.html", year=copyrightYear)

@app.route("/Contact", methods=["GET", "POST"])
def contact():
    message = None
    if request.method == "POST":
        subject = request.form["subject"]
        sender = "Anonymous Person" if request.form["email"] == "" else request.form["email"]
        message = f"{request.form['message']}<br><br>This message was sent by : {sender}"

        sendEmail(message, subject, "contact@bytepicks.com", "contact@bytepicks.com")
        message = "Thank you for contacting us!"

    return render_template("contact.html", year=copyrightYear, message=message)

if __name__ == "__main__":
    app.run()
