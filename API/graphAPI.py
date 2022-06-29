import webbrowser
from config import CLIENT_SECRET
import msal
import os
import app


GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0/'
SCOPES = ['User.Read', 'Calendars.ReadWrite']


def generate_access_token_response(application_id, SCOPES):
    """ Uses Outlook's Graph api to generate the user's access token reponse that contains the user's access token
    
        Keyword arguments:\n
        application_id      -- The outlook application id found in Azure\n
        SCOPES              -- The permissions that the app has access to
    """
    cache = msal.SerializableTokenCache()
    if os.path.exists('api_token_access.bin'):
        cache.deserialize(open('api_token_access.bin', 'r').read())

    
    client = msal.PublicClientApplication(client_id=application_id, token_cache=cache)
    accounts = client.get_accounts()
    if accounts:
        token_response = client.acquire_token_silent(SCOPES, accounts[0])
    else:
        flow = client.initiate_device_flow(scopes=SCOPES)
        auth_code = flow['user_code']
        app.send_direct_message(f"Your Authentication Code : {auth_code}")
        webbrowser.open(flow['verification_uri'])
        token_response = client.acquire_token_by_device_flow(flow)
    
    with open('api_token_access.bin', 'w') as f:
        f.write(cache.serialize())

    return token_response

def generate_access_token(application_id, SCOPES):
    """ Generates the user's access token by using generate_access_token_response
    
        Keyword arguments:\n
        application_id      -- The outlook application id found in Azure\n
        SCOPES              -- The permissions that the app has access to
    """
    token_response = generate_access_token_response(application_id, SCOPES)
    return token_response['access_token']

