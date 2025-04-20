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


import hashlib


def generate_event_id(name, date_str):
    """
    Generate a unique Google Calendar event ID based on the name and birthday.
    The ID must be between 5 and 1024 characters long and only include valid characters.
    """
    unique_str = f"{name}-{date_str}".lower()
    return hashlib.md5(unique_str.encode('utf-8')).hexdigest()


def create_birthday_event(calendar_service, name, date_str):
    if len(date_str) == 5:
        date_str = f"1970-{date_str}"  # Handle birthdays without a year

    # Handle Feb 29 birthdays specially
    if date_str.endswith("-02-29"):
        rrule = 'RRULE:FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=-1'
    else:
        rrule = 'RRULE:FREQ=YEARLY'

    event_id = generate_event_id(name, date_str)

    event = {
        'id': event_id,
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

    try:
        # Try to insert the event. If the ID already exists, an error will occur.
        created = calendar_service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        print(f"Created event for {name}’s birthday on {date_str}.")
        return created.get('id')
    except Exception as e:
        # Handle case where event already exists
        if 'duplicate' in str(e).lower():
            print(f"Event for {name}’s birthday on {date_str} already exists. Skipping.")
        else:
            print(f"An error occurred: {e}")
        return None


@click.group()
def bdays():
    pass

@bdays.command()
def sync():
    creds = get_credentials()
    peoples_service = build('people', 'v1', credentials=creds)
    calendar_service = build('calendar', 'v3', credentials=creds)

    birthdays = list_birthdays(peoples_service)

    for name, date in birthdays:
        create_birthday_event(calendar_service, name, date)


if __name__ == '__main__':
    cli()
