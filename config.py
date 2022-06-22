import os
from dotenv import load_dotenv
load_dotenv()

SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
slack_token = os.getenv('SLACK_BOT_TOKEN')
user_token = os.getenv('SLACK_USER_TOKEN')
VERIFICATION_TOKEN = os.getenv('VERIFICATION_TOKEN')


DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY')
FLASK_ADMIN_SWATCH = 'darkly'