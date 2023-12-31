from googleapiclient.discovery import build
import os


API_KEY = os.environ['YT_API_KEY']
service = build('youtube', 'v3', developerKey=API_KEY)
service.close()