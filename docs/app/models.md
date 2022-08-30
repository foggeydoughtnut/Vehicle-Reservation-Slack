# [Models](../../app/models.py)  
This project uses [SQLAlchemy](https://www.sqlalchemy.org/) for its ORM.  
=
## Vehicle Model  
### Columns  
- **id** - int  
- **name** - string (unique = True)  
- **calendarID** - string (unique = True)  
- **calendarGroupID** - string (unique = False)  
---
## User Model  
### Columns  
- **id** - int  
- **username** - string (unique = True)
- **password** - string  
### Methods  
`set_password(self, password)`  
 - Sets the User's password_hash to the password after it has been hashed.  

`check_password(self, password)`  
- Hashes the password parameter and checked the hash sequence against the one stored in the database.  