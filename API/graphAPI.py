import webbrowser
import msal
import os
import app

GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0/'
SCOPES = ['User.Read', 'Calendars.ReadWrite']


def generateAccessTokenResponse(application_id, SCOPES):
    """ Uses Outlook's Graph api to generate the user's access token reponse that contains the user's access token
    
        Keyword arguments:\n
        application_id      -- The outlook application id found in Azure\n
        SCOPES              -- The permissions that the app has access to
    """
    access_token_cache = msal.SerializableTokenCache()
    if os.path.exists('api_token_access.json'):
        access_token_cache.deserialize(open('api_token_access.json', 'r').read())
    client = msal.PublicClientApplication(client_id=application_id, token_cache=access_token_cache)
    accounts = client.get_accounts()
    authCode = ''
    if accounts:
        token_response = client.acquire_token_silent(SCOPES, accounts[0])
    else:
        flow = client.initiate_device_flow(scopes=SCOPES)
        authCode = flow['user_code']
        app.sendDirectMessage(f"Your Authentication Code : {authCode}")
        webbrowser.open(flow['verification_uri'])
        token_response = client.acquire_token_by_device_flow(flow)
        
    
    with open('api_token_access.json', 'w') as _f:
        _f.write(access_token_cache.serialize())
    return token_response

def generateAccessToken(application_id, SCOPES):
    """ Generates the user's access token by using generateAccessTokenResponse
    
        Keyword arguments:\n
        application_id      -- The outlook application id found in Azure\n
        SCOPES              -- The permissions that the app has access to
    """
    token_response = generateAccessTokenResponse(application_id, SCOPES)
    return token_response['access_token']

