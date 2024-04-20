from collections import namedtuple
from datetime import datetime, timedelta
import os.path
import pdb
import re
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Project imports
from insta import ParsedPost

# https://docs.google.com/spreadsheets/d/1Lzv5nxedHZdkPOKd-pLdd_F7D45q-nl6wKUn9gwEtsw
SPREADSHEET_ID = "1Lzv5nxedHZdkPOKd-pLdd_F7D45q-nl6wKUn9gwEtsw"
RANGE_NAME = "Raw data!A1:H1000"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TOKEN_FILE = "secret/sheets_token.json"
CREDS_FILE = "secret/sheets_secret.json"
def read_from_spreadsheet(sheet_client):
    result = (
        sheet_client.values()
        .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
        .execute()
    )

    rows = result.get("values", [])
    # skip header
    rows = rows[1:]

    return [ParsedPost(
        date = row[0],
        gym_location = row[1],
        grade = row[2],
        photo_url = row[3],
        reel_url = row[4],
        account_name = row[5],
        caption = row[6],
        time = row[7]
        ) for row in rows]

    

def write_to_spreadsheet(sheet_client, parsed_posts:List[ParsedPost]):
    """
    Fully overwrite the spreadsheet content.
    return true iff write is successful
    """
    values = [
        ["Date", "Gym", "Grade", "Photo", "Reel","Account name","Caption", "Time"],
    ]

    parsed_posts_tuples = [[
        post.date,
        post.gym_location,
        post.grade,
        post.photo_url,
        post.reel_url,
        post.account_name,
        post.caption,
        post.time
        ] for post in parsed_posts]
    values.extend(parsed_posts_tuples)

    request = sheet_client.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="RAW",
        body={"values": values}
    )
    response = request.execute()
    return 'updatedCells' in response

def get_sheet_client():
    # Adapted from https://developers.google.com/sheets/api/quickstart/python
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
               CREDS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())

    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets()