from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from datetime import datetime, timezone
from sqlalchemy.orm import sessionmaker
from collections import OrderedDict
import json, base64, os, requests

AMOUNT = {"daily": 50, "weekly": 75, "monthly": 100, "yearly": 150}
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

engine = create_engine("sqlite:///newsletter.db", echo=True)
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

def getVideos(time, language):
    with open(f"{time}.json", "r") as file:
        rawVideos = json.load(file)
        allVideos = rawVideos[language].items()

    return OrderedDict(list(allVideos)[:AMOUNT[time]])

def formatViewCount(number):
    if number / 1_000_000_000 > 1:
        return str(round(number / 1_000_000_000, 1)) + "B"
    elif number / 1_000_000 > 1:
        return str(round(number / 1_000_000, 1)) + "M"
    elif number / 1_000 > 1:
        return str(round(number / 1_000, 1)) + "K"
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

def sendEmail(body, subject, receiver, sender):
    creds = Credentials.from_authorized_user_file("token.json", scopes=SCOPES)

    service = build("gmail", "v1", credentials=creds)
    rawMessage = f"Content-Type: text/html; charset=utf-8\nFrom: {sender}\nTo: {receiver}\nSubject: {subject}\n\n{body}"
    encodedMessage = base64.urlsafe_b64encode(rawMessage.encode()).decode("utf-8")

    service.users().messages().send(userId="me", body={"raw": encodedMessage}).execute()
    service.close()

def updateToken():
    with open('token.json', 'r') as token:
        credsData = json.load(token)
        creds = Credentials.from_authorized_user_info(credsData)

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                
def getMessage(email, time, language, token):
   return f"""
	<!DOCTYPE html>
	<html lang="en-US">
	<head>
	  <style>
		 body {{
		   font-family: 'Verdana', sans-serif;
		   margin: 20px;
		   padding: 20px;
		 }}
		 p {{
		   font-size: 18px;
		   margin-bottom: 15px;
		 }}
		 a {{
		   color: #007bff;
		   text-decoration: none;
		   font-weight: bold;
		 }}
		 a:hover {{
		   text-decoration: underline;
		   color: #0056b3;
		 }}
		 button {{
		   background-color: #0b89a8;
		   color: #f9f9f9;
		   border-radius: 5px;
		   transition: 0.5s ease;
		   font-size: 20px;
		   padding: 8px 13px;
		   margin: 10px 100px;
		   border: none;
		 }}
		 button:hover {{
		   cursor: pointer;
		   background-color: #157a94;
		   color: #f0f0f0;
		   scale: 1.075;
		   transition: 0.5s ease;
		 }}
	  </style>
	</head>
	<body>
	  <center>
		 <p>Hello there!</p>
		 <p>We spotted you peeking into the exciting world of Byte Picks, and guess what? We're thrilled to have you join!</p>
		 <p>One final step before you embark on your Byte Picks journey: confirm your email address by clicking the button below. It's very simple.</p>
		 <p>if you haven't signed up. This email might have found its way to you by mistake. Just disregard it and continue your day with the wind in your sails (or Wi-Fi signal, whichever you prefer).</p>
		 <a href='https://bytepicks.com/submit?user={email}&token={token}'><button>Confirm My Email!</button></a>
		 <br><p>We can't wait to have you on board!</p>
	  </center>
	</body>
	</html>
   """
