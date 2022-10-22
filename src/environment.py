"""
Retrieving data from an environment file
"""

import os
from dotenv import load_dotenv


load_dotenv('.env')

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
GMAIL_USER_ID = os.getenv('GMAIL_USER_ID')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
ZWIFT_ACTIVITY_DIR = os.getenv('ZWIFT_ACTIVITY_DIR')
