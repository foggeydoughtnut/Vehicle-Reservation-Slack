# [Calendar.py](../../api/Calendar.py)  
`generate_headers()`  
- Used for the headers in Microsoft's graph api.  
- Uses the `generate_access_token` method to get the access_token then uses that in the headers' dictionary.  
---
`construct_event_detail(event_name, **event_details)`  
- **Parameters**  
  1. **event_name**  
      - The calendar event's name
      
  2. ****event_details**  
      - The details for the event (start_time, end_time, description, attendees)  
- Constructs a calendar event with the name and details given.  
- **Returns** the request body that was constructed.  
---  
`schedule_event(calendar_group_id, calendar_id, start_time, end_time, users_name)`  
- **Parameters**  
  1. **calendar_group_id**  
      - The group id for the Outlook calendar  
  2. **calendar_id**  
      - The id for the Outlook calendar  
  3. **start_time**  
      - The start time for the reservation  
  4. **end_time**  
      - The end time for the reservation  
  5. **users_name**  
      - The name for the reservee  
- Uses Outlook's api to schedule an event for the calendar specified by the calendar_id and calendar_group_id with the information provided.  
- **Returns** dictionary with ERROR property if reservation is made before the current time.  
- **Returns** dictionary with SUCCESS property if reservation is successfully made and no errors are found.  
- **Returns** ERROR if an error occurs when reserving the vehicle.  
---  
`list_specific_calendar_in_group_events(calendar_group_id, calendar_id)`  
- **Parameters**  
  1. **calendar_group_id**  
      - The group id for the Outlook calendar  
  2. **calendar_id**  
      - The id for the Outlook calendar  
- Uses the outlook graph api to get the events of a specific calendar in a calendar group.  
- **Returns** the events happening that day in an object with the properties of *webLink, start, end, event{i}*
>Note: `events` variable contains all the calendar information. I only use some information in it.
- **Information extracted from `events`**
  1. **webLink**  
      - The url to go to the event on the Outlook calendar  
  2. **start**  
      - The start time for the event  
  3. **end**  
      - The end time for the event  
---
`construct_calendar_events_block(events, vehicle_name)`  
- **Parameters**  
    1. **events**  
      - An object of events that is found from the `list_specific_calendar_in_group_events` function. 
    2. **vehicle_name**  
      - The vehicle name that was selected to get the reservations for.  
- Constructs the reservations_results slack block that is used to display the results of the reservations command. 
- **Returns** an object with the property `reservations` that is a boolean. True if there were any reservations, false otherwise.  
- It cleans up the start and end time by removing the microseconds and date, then it converts the time from military time (15:00) to standard time (03:00 PM)  
- It adds the data from the events (start_time, end_time, and url) and adds that to the reservations_dict.  
- It writes the reservations_dict to the reservations_results slack block in the blocks array for each event in events.  
---  
`check_if_reservation_available(calendar_group_id, calendar_id, start_time, end_time)`  
- **Parameters**  
    1. **calendar_group_id**  
      - The id for the group that the calendar is in  
    2. **calendar_id**  
      - The id for the Outlook calendar  
    3. **start_time**  
      - The start_time of the reservation  
    4. **end_time**  
      - The end_time of the reservation  
- Checks if the call to the graph api for getting events from start_time to end_time is an empty array.  
- **Returns** true or false depending on if there are events in the array or not. True if events array is empty, false otherwise.  


