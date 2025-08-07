from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import sessionmaker
from email.mime.text import MIMEText
from collections import OrderedDict
from dotenv import load_dotenv
import os, json, smtplib, ssl
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

AMOUNT = {"daily": 50, "weekly": 100, "monthly": 150, "yearly": 250}
NEWSLETTER_PASSWORD = os.environ.get("NEWSLETTER_PASSWORD")
CONTACT_PASSWORD = os.environ.get("CONTACT_PASSWORD")
SMTP_SERVER = "mail.bytepicks.com"
SMTP_PORT = 587

engine = create_engine("sqlite:///server/data/newsletter.db", echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()


class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    token = Column(String, nullable=False)
    time = Column(String)
    language = Column(String)


class PendingUser(Base):
    __tablename__ = "PendingUser"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    token = Column(String, nullable=False)
    time = Column(String)
    language = Column(String)


def get_videos(time: str, language: str, top: int = 0) -> dict:
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', f'{time}.json')
    
    with open(file_path, "r", encoding="utf-8") as file:
        all_videos = json.load(file).get(language, {}).items()

    slice_amount = top if top else AMOUNT[time]
    return OrderedDict(list(all_videos)[:slice_amount])


def format_view_count(number: int) -> str:
    if number / 1_000_000_000 > 1:
        return str(round(number / 1_000_000_000, 1)) + "B"
    elif number / 1_000_000 > 1:
        return str(round(number / 1_000_000, 1)) + "M"
    elif number / 1_000 > 1:
        return str(round(number / 1_000, 1)) + "K"
    else:
        return str(number)


def format_duration(duration: str) -> str:
    hours, minutes, seconds = map(int, duration.split(":"))
    if hours == 0 and minutes < 10:
        return f"{minutes}:{seconds:02d}"
    elif hours == 0:
        return f"{minutes:02d}:{seconds:02d}"
    else:
        return duration


def send_email(body: str, subject: str, receiver: str, sender: str):
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    context = ssl.create_default_context()
    password = NEWSLETTER_PASSWORD if sender == "newsletter@bytepicks.com" else CONTACT_PASSWORD
    with smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT)) as server:
        server.starttls(context=context)
        server.login(sender, password)
        server.sendmail(sender, receiver, message.as_string())


def get_message(email: str, token: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="en-US">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Confirm Your Email</title>
      <style>
        a.button:hover {{
          background-color: #157a94 !important;
        }}
      </style>
    </head>
    <body style="font-family: 'Verdana', sans-serif; margin: 0; padding: 40px; background-color: #f9f9f9;">
      <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; text-align: center;">
        <p style="font-size: 18px; margin-bottom: 15px; line-height: 1.6;">Hello there!</p>
        <p style="font-size: 18px; margin-bottom: 15px; line-height: 1.6;">We spotted you peeking into the exciting world of Byte Picks, and guess what? We're thrilled to have you join!</p>
        <p style="font-size: 18px; margin-bottom: 25px; line-height: 1.6;">One final step before you embark on your Byte Picks journey: confirm your email address by clicking the button below. It's very simple.</p>
        <a href='https://bytepicks.com/newsletter/submit?user={email}&token={token}'
           class="button"
           target="_blank"
           style="background-color: #0b89a8; color: #f9f9f9; border-radius: 5px; font-size: 25px; padding: 13px 25px; text-decoration: none; font-weight: bold; display: inline-block;">
           Confirm My Email!
        </a>
        <p style="font-size: 14px; margin-top: 25px; margin-bottom: 15px; color: #555555; line-height: 1.6;">If you haven't signed up, this email might have found its way to you by mistake. Just disregard it and continue your day with the wind in your sails (or Wi-Fi signal, whichever you prefer).</p>
        <p style='font-size: 18px; margin-top: 30px; margin-bottom: 10px; line-height: 1.6;'>We can't wait to have you on board!</p>
      </div>
    </body>
    </html>
    """
