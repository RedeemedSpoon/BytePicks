import os
from google.api_core import exceptions as google_exceptions
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'


def get_credentials():
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except google_exceptions.RefreshError as e:
            if e.args[0] == 'Timed out fetching refresh token':
                return refresh_and_store_credentials()
            else:
                raise e
        return creds
    else:
        return refresh_and_store_credentials()


def refresh_and_store_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=5000)

    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())

    return creds


if __name__ == '__main__':
    credentials = get_credentials()
    print('Credentials obtained successfully!')
