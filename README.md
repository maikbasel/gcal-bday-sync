# Google Calendar Birthday Sync

<!-- TOC -->
* [Google Calendar Birthday Sync](#google-calendar-birthday-sync)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
  * [Usage](#usage)
<!-- TOC -->

This tool exists because Google decided to stop automatically syncing birthdays from Contacts to Calendar due to legal
regulations in Germany (
see [details here](https://support.google.com/calendar/answer/13748346?hl=en&sjid=2163152615913692385-EU)). If you’re
annoyed by this change and want those birthdays back on your calendar as proper events, this script has you covered.

## Prerequisites

1. Create a new project in the [Google Cloud Console](https://console.cloud.google.com/).
2. Navigate to **`APIs and Services > Library`** and enable both the **Google People API** and the
   **Google Calendar API** for your project.
3. Go to **`APIs and Services > OAuth consent screen`** and configure your app as either internal or external.
4. In **`APIs and Services > OAuth consent screen > Audience`**, specify the users who will have access to the app.
5. Under **`APIs and Services > OAuth consent screen > Clients`**, create an OAuth 2.0 Client ID for a desktop
   application.
6. Download the OAuth Client JSON file and save it to the following path: **`gcal_bday_sync/client_secret.json`**.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/maikbasel/gcal-bday-sync.git
   cd gcal-bday-sync
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the project in editable mode:
   ```bash
   pip install -e .
   ```

## Usage

The `bdays` command serves as the main entry point for this tool. Below are descriptions of what it can do.

Run the following command to start syncing birthdays:

```bash
bdays sync
```

By default, this will:

1. Authenticate your Google account (using the provided credentials).
2. Fetch the list of birthdays from Google Contacts.
3. Add matching birthday events to your Google Calendar.
