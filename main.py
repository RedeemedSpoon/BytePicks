from flask import Flask, render_template, jsonify, request, send_file
from datetime import datetime
import json, secrets, string
from utils import *

TIME = ["daily", "weekly", "monthly", "yearly"]
LANGUAGE = ["EN", "FR", "ES", "RU", "HI"]

app = Flask(__name__)
copyright_year = datetime.now().year


@app.teardown_request
def teardown_request(exception=None):
    session.close()


@app.route("/")
def home():
    with open("data/daily.json", "r") as file:
        home_thumbnails = json.load(file)["EN"]

    return render_template("home.jinja", year=copyright_year, videos=home_thumbnails)


@app.route("/dashboard")
def dashboard():
    time = request.args.get("time", default="daily")
    language = request.args.get("lang", default="EN")
    if time not in TIME or language not in LANGUAGE:
        return render_template("error.jinja", year=copyright_year), 404

    videos = get_videos(time, language)
    return render_template(
        "dashboard.jinja",
        year=copyright_year,
        videos=videos,
        time=time,
        language=language,
        format_duration=format_duration,
        format_view_count=format_view_count,
    )


@app.route("/api-docs")
def api_docs():
    return render_template("api-docs.jinja", year=copyright_year)


@app.route("/api/request")
def api_request():
    time = request.args.get("time", default="daily")
    language = request.args.get("lang", default="EN")
    top = request.args.get("top", default=25, type=int)

    if time in TIME and language in LANGUAGE and top > 0:
        response = {
            "Request": f"The top {top} {time} videos in {language}",
            "Date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Results": list(get_videos(time, language, top).values()),
        }
    else:
        response = {"Error": "You send an invalid request."}

    return jsonify(response)


@app.route("/newsletter", methods=["GET", "POST"])
def newsletter():
    message = None
    email = ""

    if request.method == "POST":
        email = request.form["email"]
        if session.query(User).filter_by(email=email).first():
            message = "This Email is Already Registered."
        else:
            if session.query(PendingUser).filter_by(email=email).first():
                message = "This Email is on the Pending List."
            else:
                try:
                    language = request.form["language"]
                    time = request.form["time"]
                    token = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
                    message = get_message(email, token)
                    send_email(message, "Byte Picks : Please Confirm Your Email", email, "newsletter@bytepicks.com")
                except:
                    message = "You Gave An Invalid Email."
                else:
                    message = "Please Check Your Inbox!"
                    session.add(PendingUser(email=email, time=time, language=language, token=token))
                    session.commit()

    return render_template("newsletter.jinja", year=copyright_year, message=message, email=email)


@app.route("/newsletter/<instruction>", methods=["GET", "POST"])
def modify_newsletter(instruction):
    email = request.args.get("user", default="")
    token = request.args.get("token", default=None)

    user = None
    pending_user = None
    message = None

    if instruction not in ["submit", "edit", "delete"]:
        return render_template("error.jinja", year=copyright_year), 404

    if token is None or email == "":
        message = "Missing Token or Email."
    else:
        user = session.query(User).filter_by(email=email, token=token).first()
        pending_user = session.query(PendingUser).filter_by(email=email).first()

    if instruction == "submit":
        if user:
            message = "Email Already Registered!"
        else:
            if pending_user:
                session.add(
                    User(
                        email=pending_user.email,
                        time=pending_user.time,
                        language=pending_user.language,
                        token=pending_user.token,
                    )
                )
                session.delete(pending_user)
                session.commit()
                message = "Thank You for Subscribing!"
            else:
                message = "This Email Does not Exist."

    elif instruction == "edit" and request.method == "POST":
        if user:
            user.time = request.form["time"]
            user.language = request.form["language"]
            session.commit()
            message = "Preference Updated!"
        else:
            message = "Incorrect Token or Email."

    elif instruction == "delete":
        if user:
            session.delete(user)
            session.commit()
            message = "Successfully Unsubscribed!"
        else:
            message = "Incorrect Token or Email."

    return render_template("newsletter.jinja", year=copyright_year, message=message, email=email)


@app.route("/download")
def download():
    return send_file("channels.csv", as_attachment=True)


@app.route("/behind-the-scene")
def behind_the_scene():
    return render_template("behind-the-scene.jinja", year=copyright_year)


@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy-policy.jinja", year=copyright_year)


@app.route("/about-us")
def about_us():
    return render_template("about-us.jinja", year=copyright_year)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    message = None
    if request.method == "POST":
        subject = request.form["subject"]
        sender = "Anonymous Person" if request.form["opt-email"] == "" else request.form["opt-email"]
        message = f"{request.form['message']}<br><br>This message was sent by : {sender}"

        send_email(message, subject, "contact@bytepicks.com", "contact@bytepicks.com")
        message = "Thank you for contacting us!"

    return render_template("contact.jinja", year=copyright_year, message=message)


@app.errorhandler(404)
def bad_request(e):
    return render_template("error.jinja", year=copyright_year), 404


if __name__ == "__main__":
    app.run()
