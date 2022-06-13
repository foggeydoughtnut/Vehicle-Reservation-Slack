# Vehicle Reservation app for Slack

## Setup  
If there is no 
### Create Admin User  
In python terminal import User from models and import db_session from database. Create user and set the password for the user. Then add the user to the db then commit.  
#### Python Code:  
">>> from models import User"  
">>> from database import db_session"   
">>> {user} = User('{Insert Username}')"  
">>> {user}.set_password('{Insert Password}')"  
">>> db_session.add({user})"  
">>> db_session.commit()"  


## Running the Application  
