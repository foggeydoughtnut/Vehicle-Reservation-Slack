# Vehicle Reservation app for Slack

## Setup  
Install everything needed with poetry  
Run the app.py
Then navigate to localhost:3000/login and login to the admin page with username: admin password: password  
Then from the admin (/admin) page you can add vehicles and create admin users    

## Create Admin User  
When you run the app.py for the first time it will make a admin account with username: admin and password: password.  
With that you can log into the admin page and create a more secure admin account.  

## Getting vehicle's calendar id and calendar group id  
Go to the following link https://developer.microsoft.com/en-us/graph/graph-explorer#  
Sign in to the account that has all of the calendars needed.  
Run the following get query with the route: https://graph.microsoft.com/v1.0/me/calendarGroups to get all of the calendar groups for that account.  
From there find the calendar group that contains the calendars for the vehicles. The id will be the calander group id in the database.  
  
Run the following get query with the route: https://graph.microsoft.com/v1.0/me/calendars to get all of the calendars for the account.  
From there find the calendars for the vehicles. The calendar id for that vehicle will be the id value in that query for the vehicle's calendar.  
### Tests  
This repository uses Pytest.  
To run the tests navigate to base directory.  
Run the following command
```
pytest
```
To generate a coverage report, run the following:  
```
coverage run -m pytest and then any tests to would like to run with coverage (ex. tests/test_app.py tests/test_calendar.py)  
coverage report or coverage html
```
Note:  
Whenever you commit to the repository it will automatically run all of the tests that pytest can find and make sure that they pass in order for the commit to go through.  
To commit without testing (useful for when you just change markdown files and it will get mad for the spaces after a line) run  
git commit -m "" --no-verify
