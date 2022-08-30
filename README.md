# Vehicle Reservation app for Slack

## Setup  
Clone the repository and navigate into the project.  
Poetry install to install all of the needed packages/modules    
Copy the .env-example into a .env file and enter the needed data  
Run the run.py
Then navigate to localhost:3000/login and login to the admin page with username: **admin** password: **password**    
Then from the admin (/admin) page you can add vehicles and create admin users  

Start ngrok (or anything similar) on port 3000 so that way traffic can be forwarded to localhost:3000.  
Download Ngrok [here](https://ngrok.com/download)  
Run the following command to start ngrok
```
ngrok http 3000
```  
![Screenshot from 2022-08-26 09-04-45](https://user-images.githubusercontent.com/78196548/186935488-277a41a0-b071-4e4d-b510-aa74124ea66c.png)

Copy the forwarding https url and go to the slack app's homepage.  
Navigate to **Event Subscriptions** and set the Request URL to be that forwarding https url with /slack/events added on to it.  
ex. https://e446-blah-blah.ngrok.io/slack/events  
![Screenshot from 2022-08-26 08-27-32](https://user-images.githubusercontent.com/78196548/186927233-688045ed-1ad8-439b-8cd5-8d1e5ea08053.png)

Navigate to **Interactivity & Shortcuts** and set the Request URL to be that forwarding https url with /interactions added to it.  
ex. https://e446-blah-blah.ngrok.io/interactions  
 ![Screenshot from 2022-08-26 08-27-44](https://user-images.githubusercontent.com/78196548/186927374-fffb86e8-08b7-4e56-a615-13ef42615254.png)

Reinstall the app to the workplace through the Install App tab

## Create Admin User  
When you run the run.py for the first time it will make a admin account with username: *admin* and password: *password*.  
With that you can log into the admin page and create a more secure admin account.  

## Getting vehicle's calendar id and calendar group id  
Go to the following link https://developer.microsoft.com/en-us/graph/graph-explorer#  
Sign in to the account that has all of the calendars needed.  
Run the following get query with the route: https://graph.microsoft.com/v1.0/me/calendars to get all of the calendars for the account.  
From there find the calendars for the vehicles. The calendar id for that vehicle will be the id value in that query for the vehicle's calendar.  

Run the following get query with the route: https://graph.microsoft.com/v1.0/me/calendarGroups to get all of the calendar groups for that account.  
From there find the calendar group that contains the calendars for the vehicles. The id will be the calander group id in the database. 
## Using the slack bot  
If you have completed all of the previous parts, your slack bot should ready to run.  
Navigate to the slack channel that has the Vehicle Reservation app. If there is no workspace with the app, go ahead and add the app through the slack website.  
Start using the slack bot by mentioning the slack bot in any public channel. (ex. @Vehicle Reservation 'insert command here')  
Currently there are 5 commands the slack bot has. A reserve command, check command, vehicles command, reservations command, and help command.  
- **Reserve command**  
  1. This is the command that is when filled out and submitted will make a reservation for the vehicle the user requested.  
- **Check command**  
  1. This command is used to see if a vehicle is available from start_time to end_time. The start_time and end_time are given to the command by the user. 
- **Vehicles command**  
  1. This command is used to see all of the vehicles in the database and checks if there are any reservations for it in the next 15 minutes.  
- **Reservations command**  
  1. This command can be used to see all of the reservations that a certain vehicle has for today.  
- **Help command**  
  1. This command displays all of the commands available and what keyword is used to invoke the command. It also gives basic information about what the command does.  

When the api access token is not in the api_token_access.bin file and a user uses the commands that need outlook's calendars for the first time, the user is sent a direct message through the Vehicle Reservations bot channel and Microsofts verification window is opened. The user needs to take the code that was sent to them and input it into the window that was opened. Then the user chooses the user that has all of the vehicles in it.  
It then will save the access token inside of the api_token_access.bin file, so that way it is saved.  
> Note: The access token will need to be for the same outlook account that we used to fill up the database.  

## Database  
This project uses [**sqlite3**](https://www.sqlite.org/docs.html) for its database.  
This project uses [**SQLAlchemy**](https://docs.sqlalchemy.org/en/14/) for its ORM.  

## Tests  
This repository uses [Pytest](https://docs.pytest.org/en/7.1.x/contents.html).  
To run the tests navigate to base directory.  
Run the following command
```
pytest
```
To generate a coverage report, run the following:  
```
coverage run -m pytest
coverage report or coverage html
```  

## Scopes  
### Slack 
#### **Bot Token Scopes**
- app_mentions:read  
- channels:history  
- chat:write  
- im:history  
#### **User Token Scopes**  
- identity.basic  

### Azure  
#### **Graph api**  
- Calendars.ReadWrite  
- User.Read  
