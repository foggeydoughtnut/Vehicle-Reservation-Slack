from webbrowser import get
import requests
import os
from API.graphAPI import generate_access_token, GRAPH_API_ENDPOINT, SCOPES
from dotenv import load_dotenv
load_dotenv()

def get_user_by_access_token(access_token):
    """ Gets the user by using the Outlook Graph api
    
        Keyword arguments:\n
        access_token      -- The access_token for the user
    """
    headers = {'Authorization' : 'Bearer ' + access_token}
    url = GRAPH_API_ENDPOINT + 'me'
    response = requests.get(url, headers=headers)
    return response.json()


def get_user():
    """ Gets the User by using the get_user_by_access_token method """
    application_id = os.getenv('APPLICATION_ID')
    access_token = generate_access_token(application_id, SCOPES)
    # access_token = get_access_token()
    # if access_token == '':
    #     access_token = set_access_token(application_id)
    return get_user_by_access_token(access_token)

def get_users_name():
    """ Uses the get_user method to find the user, then returns the name associated with that user"""
    user = get_user()
    name = user['displayName']
    return name

def get_users_email():
    """ Uses the get_user method to find the user, then returns the email associated with that user"""
    user = get_user()
    email = user['userPrincipalName']
    return email
