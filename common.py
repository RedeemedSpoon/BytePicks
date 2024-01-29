from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timezone
import json, base64, os, requests

engine = create_engine("sqlite:///data/newsletter.db", echo=True)
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
    with open(f"videos/{time}.json", "r") as file:
        timeVideos = json.load(file)

    return {key: value for key, value in timeVideos.items() if value["language"][:2] == language}


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


def sendEmail(body, subject, receiver, sender):
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", scopes=SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=5000, access_type="offline", prompt="consent")

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    rawMessage = f"Content-Type: text/html; charset=utf-8\nFrom: {sender}\nTo: {receiver}\nSubject: {subject}\n\n{body}"
    encoded_message = base64.urlsafe_b64encode(rawMessage.encode()).decode("utf-8")

    service.users().messages().send(userId="me", body={"raw": encoded_message}).execute()
    service.close()


def getNewToken(refresh_token, client_id, client_secret):
    token_endpoint = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    response = requests.post(token_endpoint, data=payload)
    return response.json()


def updateToken():
    with open("token.json", "r") as JsonFile:
        tokenInfo = json.load(JsonFile)

    expiryTime = datetime.fromisoformat(tokenInfo["expiry"]).replace(tzinfo=timezone.utc)
    currentTime = datetime.now(timezone.utc)

    if currentTime >= expiryTime:
        newTokenInfo = getNewToken(tokenInfo["refresh_token"], tokenInfo["client_id"], tokenInfo["client_secret"])
        if newTokenInfo["refresh_token"]:
            with open("token.json", "w") as JsonFile:
                json.dump(newTokenInfo, JsonFile, indent=2)
