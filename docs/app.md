# App.py  
This file is where all of the slack bot logic is handled. It is also where the Flask configuration is done.  

---  
`create_admin_user()`  
- This method creates an admin user with the username **admin** and passowrd **password** when there is no Users in the table. This is used so when the app first launches you can sign in to the admin page and create a new User with the credentials you would like to use. After you create the user you delete this insecure admin user.  
- Uses the database api to create a new user.  
---  
### MyModelView(ModelView)  
- Overides the normal Flask-Admin ModelView and adds the method is_accessible which is used to make ModelViews only show up when you are logged in to the Admin page.  
--- 
### MyUserView(ModelView)  
- Overides the normal Flask-Admin ModelView and adds the method is_accessible to add authentication to see the ModelView View.  
`create_view`  
- This function overides the default create view so that way you can create a new user without needing to hash the password manually.  
---  
`check_available(vehicle, start_time, end_time`
- **Params**  
    1. **vehicle**  
      - The vehicle that was queried  
    2. **start_time**  
      - The start_time of the check  
    3. **end_time**  
      - The end_time of the check  
- Calls the api to check_if_reservation_avaible and returns that boolean.  
---  
`get_selected_vehicle_name_from_payload(payload)`  
- **Paramas**  
    1. **payload**  
      - The payload sent from the /interactions route. 
      - This payload contains all of the information about what the user inputed including the vehicle they selected.  
- Navigates through the payload dictionary and finds the vehicle name.  
- Returns that vehicle name it found.  
---  
`get_start_end_time_from_payload(payload)`  
- **Paramas**  
    1. **payload**  
      - The payload sent from the /interactions route.  
- Finds the start_date and time and end_date and time and formats them to be in ISO 8601 format. ("yyyy-mm-ddTHH-MM-SS", ex. 2022-01-01T12:00:00)  
> Note: format needs to be in ISO 8601 format to work with outlook's api.  
---  
`reserve_vehicle(payload, selected_vehicle)`  
- **Params**  
    1. **payload**  
      - The payload sent from the /interaction route 
    2. **selected_vehicle**  
      - The vehicle that was selected to be reserved  
- Uses the api to check that the vehicle is avaible for when the user would like to reserve it. If it is, it reserves the vehicle, else, it messages the user that it is not available at that time.  
- If the start or end time is NoneTNone that means the user did not input any start_time or end_time.  
---  
`check_vehicle(payload, selected_vehicle)`  
- **Params**  
    1. **payload**  
      - The payload sent from the /interaction route 
    2. **selected_vehicle**  
      - The vehicle that the api will check if it is available  
- Checks the selected vehicle from start_time to end_time.  
---  
`get_reservations(payload, selected_vehicle)`
- **Params**  
    1. **payload**  
      - The payload sent from the /interaction route 
    2. **selected_vehicle**  
      - The vehicle that we want to get the reservations for  
- Uses the api to get all of the reservations for the selected vehicle.  
---
`create_vehicle_options_slack_block()`  
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
`get_slack_block_and_add_vehicles(path_to_file)`  
- **Params**  
    1. **path_to_file**  
      - The path the the slack_block file is located at.  
- This method gets the slack block from the file specified by the paramater and then adds all of the vehicles options to that block from. The vehicle options are found from the `create_vehicle_options_slack_block` method.  
- **Returns** a slack block with the vehicle options added on to the original slack_block. 
---  
`construct_vehicles_command()`  
- Constructs the vehicles command's slack block so it includes all of the vehicles and if they are available within the next 15 minutes or not.  
- It truncates the block file first to get rid of whatever was there before it adds on to the file. That way we know we have the accurate information everytime.  
--- 
`send_reply(value)`  
- **Params**  
    1. **value**  
      - A dictionary that contains important information like team_id, event information, ect.  
      - The main important one is the event sub-dictionary as it contains the message and user.  
- This method is the method that handles the user input. It looks at the first word the user inputted and calls the appropriate method for that command.  
- If there is no command that matches it tells the user that it didn't recognize the command. It also finds a command that it matches the closest to using the difflib.get_close_matches library and tells the user what it thought they meant to type.  
--- 
`get_user_slack_id`  
- Finds the user's slack id using the users_identity method.  
--- 
`send_direct_message(response_text)`  
- **Params**  
    1. **response_text**  
      - The text that is going to be sent to the user  
- Direct messages a user with the message of the reponse text.  
- Currently used only for sending a verification code when getting outlook graph api access token.  
---  
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
