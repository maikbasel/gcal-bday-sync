import os
from datetime import datetime
from pathlib import Path

import click
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/contacts.readonly', 'https://www.googleapis.com/auth/calendar']
BASE_DIR = Path(__file__).resolve().parent
TOKEN_PATH = BASE_DIR / 'token.json'
CREDENTIALS_PATH = BASE_DIR / 'client_secret.json'


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server()
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())

    return creds


@click.group()
def cli():
    pass


@cli.command(name='bdays')
def list_birthdays():
    creds = get_credentials()
    page_size = 200
    service = build('people', 'v1', credentials=creds)

    results = service.people().connections().list(
        resourceName='people/me',
        personFields='names,birthdays',
        pageSize=page_size
    ).execute()

    connections = results.get('connections', [])

    birthdays = []
    for person in connections:
        names = person.get('names', [])
        bdays = person.get('birthdays', [])
        if names and bdays:
            name = names[0].get('displayName')
            # birthdays may include multiple formats; pick the first with date
            date = bdays[0].get('date', {})
            year = date.get('year')  # may be None
            month = date.get('month')
            day = date.get('day')
            if month and day:
                # format nicely
                if year:
                    dt = datetime(year, month, day)
                    formatted = dt.strftime('%Y‑%m‑%d')
                else:
                    formatted = f"{month:02d}-{day:02d}"
                birthdays.append((name, formatted))

    for name, date in sorted(birthdays, key=lambda x: x[1]):
        print(f"{name}: {date}")

if __name__ == '__main__':
    cli()
