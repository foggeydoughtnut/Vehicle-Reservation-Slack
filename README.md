# Vehicle Reservation app for Slack

## Setup  
Type in the following commands in the python terminal  
```
>>> from databse import init_db
>>> init_db()
```
This will create an admin user in the database right now.

If there is no admin user
### Create Admin User  
In python terminal import User and db from models. Create app and app context, then create user and set the password for the user. Then add the user to the db then commit.  
#### Python Code:  
```
>>> from app import create_app  
>>> from models import db, User
>>> app = create_app()
>>> app.app_context().push()
>>> with app.app_context():
...     db.create_all()
>>> admin = User('admin')
>>> admin.set_password('password')
>>> db.session.add(admin)
>>> db.session.commit()
```  
### Migrations  
When a column in a model changes make sure to run 
```
$ flask db migrate -m "message goes here"  
$ flask db upgrade  
```



## Running the Application  
