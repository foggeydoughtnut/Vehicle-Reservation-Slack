import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
slack_token = os.getenv('SLACK_BOT_TOKEN')
user_token = os.getenv('SLACK_USER_TOKEN')
VERIFICATION_TOKEN = os.getenv('VERIFICATION_TOKEN')
# For Outlook
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0/'
SCOPES = ['User.Read', 'Calendars.ReadWrite']
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
APPLICATION_ID = os.getenv('APPLICATION_ID')

SECRET_KEY = os.getenv('SECRET_KEY')


DEBUG = True
FLASK_ADMIN_SWATCH = 'darkly'
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)