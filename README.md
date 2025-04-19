# Google Calendar Birthday Sync

## Prerequisites

1. Create a new project in the [Google Cloud Console](https://console.cloud.google.com/).
2. Go to `APIs and Services > Library` and enable **Google People API** as well as **Google Calendar API** for your
   project.
3. Go to `APIs and Services > OAuth content screen` and configure an external or internal app.
4. Go to `APIs and Services > OAuth content screen > Audience` and add your users.
5. Go to `APIs and Services > OAuth content screen > Clients` and create an OAuth2.0 Client ID of type Desktop app.
6. Download OAuth-Client JSON and place it in [gcal-bday-sync](gcal-bday-sync/client_secret.json).

## Usage

``
python cli bdays
``