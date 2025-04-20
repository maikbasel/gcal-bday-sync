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


def list_birthdays(peoples_service):
    page_size = 200

    results = peoples_service.people().connections().list(
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

    return sorted(birthdays, key=lambda x: x[1])



def create_birthday_event(calendar_service, name, date_str):
    if len(date_str) == 5:
        date_str = f"1970-{date_str}"

    # Handle Feb 29 birthdays specially
    if date_str.endswith("-02-29"):
        rrule = 'RRULE:FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=-1'
    else:
        rrule = 'RRULE:FREQ=YEARLY'

    event = {
        'summary': f"{name}’s Birthday",
        'start': {'date': date_str},
        'end': {'date': date_str},
        'recurrence': [rrule],
        'visibility': 'private',
        'transparency': 'transparent',
        'eventType': 'birthday',
        'birthdayProperties': {
            'type': 'birthday'
        },
    }

    created = calendar_service.events().insert(
        calendarId='primary',
        body=event
    ).execute()
    return created.get('id')


@click.group()
def cli():
    pass


@cli.command(name='bdays')
def bdays():
    creds = get_credentials()
    peoples_service = build('people', 'v1', credentials=creds)
    calendar_service = build('calendar', 'v3', credentials=creds)

    # Step 1: Get the list of all birthdays
    birthdays = list_birthdays(peoples_service)

    name, date = birthdays[0]
    create_birthday_event(calendar_service, name, date)
    # Step 2: Create a birthday event for each birthday
    # for name, date in birthdays:
    #     print(name, date)
        # create_birthday_event(calendar_service, name, date)


if __name__ == '__main__':
    cli()
