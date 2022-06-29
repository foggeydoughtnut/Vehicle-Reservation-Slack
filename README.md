# Vehicle Reservation app for Slack

## Setup  
Run the app.py
Then login to the admin page with /login username: admin password: password 
Then from the admin (/admin) page you can add vehicles  
Can logout with the route /logout  

### Create Admin User  
When you run the app.py for the first time it will make a admin account with username: admin and password: password.  
From there you can log into the admin page and create a more secure admin account.  
### Migrations  
When a column in a model changes make sure to run 
```
$ flask db migrate -m "message goes here"  
$ flask db upgrade  
```



## Running the Application  
