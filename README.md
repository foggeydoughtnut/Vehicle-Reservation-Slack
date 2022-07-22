# Vehicle Reservation app for Slack

## Setup  
Run the app.py
Then navigate to localhost:3000/login and login to the admin page with username: admin password: password 
Then from the admin (/admin) page you can add vehicles  

### Create Admin User  
When you run the app.py for the first time it will make a admin account with username: admin and password: password.  
From there you can log into the admin page and create a more secure admin account.  
### Migrations  
When a column in a model changes make sure to run 
```
$ flask db migrate -m "message goes here"  
$ flask db upgrade  
```
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
