# Vehicle Reservation app for Slack

## Setup  
Poetry install   
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
Copy the forwarding https url and go to the slack app's homepage.  
Navigate to Event Subscriptions and set the Request URL to be that forwarding https url with /slack/events added on to it.  
ex. https://e446-blah-blah.ngrok.io/slack/events  
![Screenshot from 2022-08-26 08-27-32](https://user-images.githubusercontent.com/78196548/186927233-688045ed-1ad8-439b-8cd5-8d1e5ea08053.png)

Navigate to Interactivity & Shortcuts and set the Request URL to be that forwarding https url with /interactions added to it.  
ex. https://e446-blah-blah.ngrok.io/interactions  
 ![Screenshot from 2022-08-26 08-27-44](https://user-images.githubusercontent.com/78196548/186927374-fffb86e8-08b7-4e56-a615-13ef42615254.png)

Reinstall the app to the workplace through the Install App tab

## Create Admin User  
When you run the run.py for the first time it will make a admin account with username: admin and password: password.  
With that you can log into the admin page and create a more secure admin account.  

## Getting vehicle's calendar id and calendar group id  
Go to the following link https://developer.microsoft.com/en-us/graph/graph-explorer#  
Sign in to the account that has all of the calendars needed.  
Run the following get query with the route: https://graph.microsoft.com/v1.0/me/calendars to get all of the calendars for the account.  
From there find the calendars for the vehicles. The calendar id for that vehicle will be the id value in that query for the vehicle's calendar.  

Run the following get query with the route: https://graph.microsoft.com/v1.0/me/calendarGroups to get all of the calendar groups for that account.  
From there find the calendar group that contains the calendars for the vehicles. The id will be the calander group id in the database. 
### Tests  
This repository uses Pytest.  
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
