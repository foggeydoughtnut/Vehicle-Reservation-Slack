# Database Logic  
Contains the database logic so that way the database models don't have to be imported into the other files.  

--- 
`get_vehicle_names()`  
- **Returns** all of the vehicle names found in the Vehicle model  
---  
`get_vehicle_by_name(vehicle_name)`  
- **Parameters**  
    1. **vehicle_name**  
      - The vehicle_name you want to find the vehicle for.  
- **Returns** the queried vehicle from the Vehicle model based on its name  
---  
`get_all_vehicles()`  
- **Returns** all of the vehicles in the Vehicle model  
---  
`get_all_users()`  
- **Returns** all of the users in the User model  
---  
`get_user_by_id(id)`
- **Parametars**  
    1. **id**
      - The id for the user you want to find.  
- **Returns** a User from the User model based on its id.  
---  
`get_user_by_username(username)`  
- **Params**  
    1. **username**  
      - The username for the User you want to find  
- **Returns** a User from the User model based on its username  
---  
`delete_user_by_id(id)`  
- **Params**  
    1. **id**  
      - The id for the user you want to delete  
- Deletes the user from the User table based on its id.  
---  
`delete_user_by_username(username)`  
- **Params**  
    1. **username**  
      - The username for the user you want to delete  
- Deletes the user from the User table based on its username.  
---
`create_user(username, password)`  
- **Params**  
    1. **username**  
      - The username that will be used for the new User  
    2. **password**  
      - The password that will be used for the new User  
- Creates a new User and hashes the password by using the `set_password` method in the User model. Then commits and saves the user.  
- **Returns** the new user that was created  
---  
`check_if_user_exists(username)`  
- **Params**  
    1. **username**  
      - The username that is going to be used in the User query.  
- Queries the User model with the username = username, and returns if there is a user with that username.  