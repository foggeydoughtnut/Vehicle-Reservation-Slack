# [Views](../../app/views.py)  
### This is the file where all the route's logic is defined.  
---
`login()`  
- Route : `/login`  
- Valid Methods : POST and GET
- **GET /login**
    - Renders the login.html template.  
    - This is the login form that you use to sign in.  
- **POST /login**  
    - The login form POSTS to this route.  
    - Takes the username and password from the form and checks that it is valid.  
    - If it is, the user it redirected to `/admin`. Otherwise, they are redirected to `/login` and alerted that their credentials were incorrect.  
---
`logout()`  
- Route : `/logout`  
- Valid Methods : POST and GET  
- **GET /logout**  
  - The user is signed out and redirected to `/login` and success message is displayed.  
- **POST /logout**  
   - The user is signed out and redirected to `/login` and success message is displayed.  
---
`create_new_user()`  
- Route : `/create/new/user`
- Valid Methods : POST  
- **POST /create/new/user**  
  - Gets the username and password and confirm password from the form.  
  - Checks that the username doesn't exist and that the passwords match.  
  - If those checks pass then it creates the user using the `db.index.create_user` method.  
  - It then redirects to `/admin/user` if it successfully created the account.  
  - If cancel is pressed then it redirects the user to `/admin/user`  
  - If the credentials didn't match or username existed it informs the user and redirects them to `/admin/user/new`  
---  
`interactions()`  
- Route : `/interactions`  
- Valid Methods : POST  
- **POST /interactions**  
    - The route that slacks blocks call when you click the submit button.  
    - Checks what block_command_type was given, and then it calls the appropriate method for that.  
    - Slack blocks will send a post to `/interactions` everytime you change an action field. This was causing me problems because I hadn't filled out everything yet. I fixed this by adding the line  
        ```
        if payload['actions'][0]['action_id'] != 'submit':
            return {'status' : 200}
        ```
    - This makes it not do anything with the posts until you click submit on the slack block.  
---  
`event_hook(request = None)`  
- Route : `/`  
- Valid Methods : GET  
- **GET /**  
    - This route just redirects to `/login` if the request == None    
    - Slack uses this route to verify the slack blocks Event Subscriptions.  
    - This route is needed to be able to use the slack bot.   