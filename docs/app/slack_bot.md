# [Slack Bot](../../app/slack_bot.py)  

## Class **SlackBotCommands**  
- This class is just an object that has what each command is.  
---
## Class **SlackBotLogic**
`send_ephemeral_message(text, channel_id, user_id, ts_id, blocks='')`
- **Params**  
    1. **text**  
      - The message that will be sent to the user.  
    2. **channel_id**  
      - The channel the message will be sent to.  
    3. **user_id**  
      - The user that the message will be sent to.  
    4. **ts_id**  
      - The thread id that the message will be sent to.  
    5. **blocks** (optional)  
      - The slack block that will be sent.  
- Sends an ephemeral message to the user specified by the id.  
---
`find_similar_commands`  
- **Params**  
    1. command  
        - The command that was given  
- Using the difflib library it finds the closest command to what the user typed.  
---  
`get_selected_vehicle_name_from_payload(payload)`  
- **Params**  
    1. **payload**  
      - The payload sent from the /interactions route. 
      - This payload contains all the information about what the user inputted including the vehicle they selected.  
- Navigates through the payload dictionary and finds the vehicle name.  
- Returns that vehicle name it found.  
---  
`get_start_end_time_from_payload(payload)`  
- **Params**  
    1. **payload**  
      - The payload sent from the /interactions route.  
- Finds the start_date and time and end_date and time and formats them to be in ISO 8601 format. ("yyyy-mm-ddTHH-MM-SS", ex. 2022-01-01T12:00:00)  
> Note: format needs to be in ISO 8601 format to work with outlook's api.  
---  
`validate_slack_message(request)`  
- **Params**  
    1. request  
        - The request that was sent by slack  
- Validates the Slack message using the verification token. This assures that the message is coming from the correct location.  
> Note: Verification tokens will be deprecated eventually. The recommended way to do this now is by using the slack-signing-secret method instead. See https://api.slack.com/authentication/verifying-requests-from-slack for more info
---
`create_vehicle_options_slack_block(vehicle_names)`  
- **Params**  
    1. vehicle_names  
        - The names of the vehicles that are in the database
- Creates the vehicle_options array of objects that will be used in the `get_slack_block_and_add_vehicles`.  
- The structure of one of the objects is like the following:  
```
"text": {
    "type": "plain_text",
    "text": "test1"
},
"value": "value-1"
```
---
`get_slack_block_and_add_vehicles(path_to_file, vehicle_names)`  
- **Params**  
    1. **path_to_file**  
      - The path the slack_block file is located at.  
    2. **vehicle_names**  
      - The vehicle names that are in the database
- This method gets the slack block from the file specified by the parameter and then adds all the vehicles options to that block from. The vehicle options are found from the `create_vehicle_options_slack_block` method.  
- **Returns** a slack block with the vehicle options added on to the original slack_block. 
---  
`check_available(vehicle, start_time, end_time)`
- **Params**  
    1. **vehicle**  
      - The vehicle that was queried  
    2. **start_time**  
      - The start_time of the check  
    3. **end_time**  
      - The end_time of the check  
- Calls the api to check_if_reservation_available and returns that boolean.  
---  
`get_reservations(payload, selected_vehicle)`
- **Params**  
    1. **payload**  
      - The payload sent from the /interaction route 
    2. **selected_vehicle**  
      - The vehicle that we want to get the reservations for  
- Uses the api to get all the reservations for the selected vehicle.  
---
`construct_vehicles_command(vehicles)`  
- **Params**  
    1. **vehicles**  
      - The vehicles that are in the database
- Constructs the vehicles command's slack block, so it includes all the vehicles and if they are available within the next 15 minutes or not.  
- It truncates the block file first to get rid of whatever was there before it adds on to the file. That way we know we have the accurate information everytime.  
--- 
`check_vehicle(payload, selected_vehicle)`  
- **Params**  
    1. **payload**  
      - The payload sent from the /interaction route 
    2. **selected_vehicle**  
      - The vehicle that the api will check if it is available  
- Checks the selected vehicle from start_time to end_time.  
---  
`reserve_vehicle(payload, selected_vehicle)`  
- **Params**  
    1. **payload**  
      - The payload sent from the /interaction route 
    2. **selected_vehicle**  
      - The vehicle that was selected to be reserved  
- Uses the api to check that the vehicle is available for when the user would like to reserve it. If it is, it reserves the vehicle, else, it messages the user that it is not available at that time.  
- If the start or end time is NoneTNone that means the user did not input any start_time or end_time.  
---  
`get_user_slack_id`  
- Finds the user's slack id using the users_identity method.  
--- 
`send_direct_message(response_text)`  
- **Params**  
    1. **response_text**  
      - The text that is going to be sent to the user  
- Direct messages a user with the message of the response text.  
- Currently used only for sending a verification code when getting outlook graph api access token.  
---  
`handle_message_response(value, app)`  
- **Params**  
    1. **value**  
      - A dictionary that contains important information like team_id, event information, ect.  
      - The main important one is the event sub-dictionary as it contains the message and user.  
    2. **app**  
      - The flask application
- This method is the method that handles the user input. It looks at the first word the user inputted and calls the appropriate method for that command.  
- If there is no command that matches it tells the user that it didn't recognize the command, and it tries to find the closest match 
--- 