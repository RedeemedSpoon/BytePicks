from flask import Flask, render_template, jsonify, request, send_file
from datetime import datetime
import json, secrets, string
from common import *

TIME = ["daily", "weekly", "monthly", "yearly"]
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

@app.route("/dashboard")
def dashboard():
    time = request.args.get("time", default="daily")
    language = request.args.get("lang", default="EN")
    videos = getVideos(time, language)
    return render_template("dashboard.html", year=copyrightYear,
        videos=videos, time=time,language=language,
        formatDuration=formatDuration, formatViewCount=formatViewCount,
    )

@app.route("/api-docs")
def api():
    return render_template("api.html", year=copyrightYear)

@app.route("/api-request")
def apiRequest():
    time = request.args.get("time", default="daily")
    language = request.args.get("lang", default="EN")
    top = request.args.get("top", default=25, type=int)
    if time in TIME and language in LANGUAGE and top > 0:
        response = {
            "Request": f"The top {top} {time} videos in {language}",
            "Date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Result": getVideos(time, language),
        }
    else:
        response = {"Result": "You send an invalid request."}

    return jsonify(response)

@app.route("/newsletter", methods=["GET", "POST"])
def newsletter():
    message = None
    if request.method == "POST":
        email = request.form["user_email"]
        user = session.query(User).filter_by(email=email).first()
        if user:
            message = "This Email is Already Registered."
        else:
            user = session.query(PendingUser).filter_by(email=email).first()
            if user:
                message = "This Email is on the Pending List."
            else:
                try:
                    time = request.form["time"]
                    language = request.form["language"]
                    token = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
                    message = getMessage(email, time, language, token)
                    sendEmail(message, "Byte Picks : Please Confirm Your Email", email, "newsletter@bytepicks.com")
                except:
                    message = "You Gave An Invalid Email."
                else:
                    message = "Please Check Your Inbox!"
                    session.add(PendingUser(email=email, time=time, language=language, token=token))
                    session.commit()

    return render_template("newsletter.html", year=copyrightYear, message=message, email="")

@app.route("/submit", methods=["GET", "POST"])
def submit():
    token = request.args.get("token", default=None)
    email = request.args.get("user", default="")
    message = None
    if token is None or email == "":
        message = "Missing Token or Email."
    else:
        user = session.query(User).filter_by(token=token, email=email).first()
        if user:
            message = "Email Already Registered!"
        else:
            user = session.query(PendingUser).filter_by(email=email).first()
            if user:
                session.add(User(email=user.email, time=user.time, language=user.language, token=user.token))
                session.delete(user)
                session.commit()
                message = "Thank You for Subscribing!"
            else:
                message = "This Email Does not Exist."

    return render_template("newsletter.html", year=copyrightYear, message=message, email="")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    token = request.args.get("token", default=None)
    email = request.args.get("user", default="")
    message = None
    if request.method == "POST":
        if token is None or email == "":
            message = "Missing Token or Email."
        else:
            user = session.query(User).filter_by(token=token, email=email).first()
            if user:
               user.time = request.form["time"]
               user.language = request.form["language"]
               message = "Preference Updated!"
            else:
               message = "Incorrect Token or Email."

    return render_template("newsletter.html", year=copyrightYear, message=message, email=email)

@app.route("/drop", methods=["GET", "POST"])
def drop():
    token = request.args.get("token", default=None)
    email = request.args.get("user", default="")
    message = None
    if token is None or email == "":
        message = "Missing Token or Email."
    else:
        user = session.query(User).filter_by(token=token, email=email).first()
        if user:
            session.delete(user)
            session.commit()
            message = "Sucessfully Unsubscribed!"
        else:
            message = "Incorrect Token or Email."

    return render_template("newsletter.html", year=copyrightYear, message=message, email="")

@app.route("/download")
def download():
	return send_file("channels.csv", as_attachment=True)

@app.route("/explaination")
def explaination():
    return render_template("explaination.html", year=copyrightYear)

@app.route("/privacy-policy")
def privacyPolicy():
    return render_template("privacy-policy.html", year=copyrightYear)

@app.route("/about-us")
def aboutUs():
    return render_template("about-us.html", year=copyrightYear)

@app.route("/contact", methods=["GET", "POST"])
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
