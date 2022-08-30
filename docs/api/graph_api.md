# graph_api  
`generate_access_token_response(application_id, SCOPES)`  
- Parameters  
    1. **application_id**  
      - The outlook application id found in Azure  
    2. **SCOPES**  
      - The permissions that the app was given.  
- Reads the api_token_access.bin and checks if there is an account in the cache. If there is an account then it uses the client.acquire_token_silent to grab the access token response without having to have the user sign in.  
- If there is no access token for that user, it acquires a token by using the device flow. The user has to log into the user they want to use and give permission for the permissions that the app wants to use.  
- It then caches the user's access token inside the api_token_access.bin file.  
>Note: Since the application will only have one user, it just grabs the first account from the api_token_access.bin.  
- **Returns** the token response  
---  
`generate_access_token(application_id, SCOPES)`  
- Parameters  
    1. **application_id**  
      - The outlook application id found in Azure  
    2. **SCOPES**  
      - The permissions that the app was given.  
- Takes the token response from `generate_access_token_reponse` and returns the access token.  