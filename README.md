# Vehicle Reservation app for Slack

## Setup  
Type in the following commands in the python terminal  
'>>> from databse import init_db'  
'>>> init_db()'  
This will create an admin user in the database right now.

If there is no admin user
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
