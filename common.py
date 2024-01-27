from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json, smtplib, os


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


def initializeEmail():
    global senderEmail, senderPassword, smtpServer, smtpPort, server
    senderEmail = "newsletter@bytepicks.com"
    senderPassword = os.environ.get("BP_PASSWORD")
    smtpServer = "smtp.bytepicks.com"
    smtpPort = 587
    server = smtplib.SMTP(smtpServer, smtpPort)
    server.starttls()
    server.login(senderEmail, senderPassword)


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
