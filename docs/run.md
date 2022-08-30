# [run.py](../run.py)  
This file is where all the slack bot logic is handled. It is also where the Flask configuration is done.  

---  
`create_admin_user()`  
- This method creates an admin user with the username: **admin** and password: **password** when there is no Users in the table. This is used so when the app first launches you can sign in to the admin page and create a new User with the credentials you would like to use. After you create the user you delete this insecure admin user.  
- Uses the database api to create a new user.  
---  
### MyModelView(ModelView)  
- Overrides the normal Flask-Admin ModelView and adds the method is_accessible which is used to make ModelViews only show up when you are logged in to the Admin page.  
--- 
### MyUserView(ModelView)  
- Overrides the normal Flask-Admin ModelView and adds the method is_accessible to add authentication to see the ModelView View.  
`create_view`  
- This function overrides the default create view so that way you can create a new user without needing to hash the password manually.  
---  
### MyHomeView(AdminIndexView)  
- Overrides the base admin index view to contain the [admin/index.html](../app/templates/admin/index.html) template.  
--- 
`handle_message` and `send_reply`  
- The `@slack_events_adapter.on("app_mention")` listens for when the slack bot is mentioned. It then will take the message's data that was sent and calls the `handle_message_reponse` in [slack_bot.py](../app/slack_bot.py)
