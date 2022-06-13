import requests
import os
from API.graphAPI import generateAccessToken, GRAPH_API_ENDPOINT, SCOPES
from dotenv import load_dotenv
load_dotenv()

def getUserByAccessToken(access_token):
    """ Gets the user by using the Outlook Graph api
    
        Keyword arguments:\n
        access_token      -- The access_token for the user
    """
    headers = {'Authorization' : 'Bearer ' + access_token}
    url = GRAPH_API_ENDPOINT + 'me'
    response = requests.get(url, headers=headers)
    return response.json()


def getUser():
    """ Gets the User by using the getUserByAccessToken method """
    application_id = os.getenv('APPLICATION_ID')
    access_token = generateAccessToken(application_id, SCOPES)
    return getUserByAccessToken(access_token)

def getUsersName():
    """ Uses the getUser method to find the user, then returns the name associated with that user"""
    user = getUser()
    name = user['displayName']
    return name

def getUsersEmail():
    """ Uses the getUser method to find the user, then returns the email associated with that user"""
    user = getUser()
    email = user['userPrincipalName']
    return email
