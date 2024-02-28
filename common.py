from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from datetime import datetime, timezone
from sqlalchemy.orm import sessionmaker
import json, base64, os, requests


engine = create_engine("sqlite:///newsletter.db", echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    token = Column(String, nullable=False)
    time = Column(String)
    language = Column(String)

def getVideos(time, language):
    with open(f"{time}.json", "r") as file:
        timeVideos = json.load(file)

    return timeVideos[language]

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
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    creds = Credentials.from_authorized_user_file("token.json", scopes=SCOPES)

    service = build("gmail", "v1", credentials=creds)
    rawMessage = f"Content-Type: text/html; charset=utf-8\nFrom: {sender}\nTo: {receiver}\nSubject: {subject}\n\n{body}"
    encoded_message = base64.urlsafe_b64encode(rawMessage.encode()).decode("utf-8")

    service.users().messages().send(userId="me", body={"raw": encoded_message}).execute()
    service.close()

def updateToken():
    with open('token.json', 'r') as token:
        credsData = json.load(token)
        creds = Credentials.from_authorized_user_info(credsData)

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
