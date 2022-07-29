import requests
import os
from time import strftime
import datetime
import API.graphAPI
import API.User
from dotenv import load_dotenv
load_dotenv()
from time import strftime


application_id = os.getenv('APPLICATION_ID')


def generate_headers():
    access_token = API.graphAPI.generate_access_token(application_id, API.graphAPI.SCOPES)
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    return headers


def construct_event_detail(event_name, **event_details):
    """ Constructs a calendar event with the name and details given

        Keyword arguments:\n
        event_name      -- The calendar event's name\n
        event_details   -- The details for the event (start_time, end_time, description, attendees)
    """
    request_body = {
        'subject' : event_name
    }
    for key, value in event_details.items():
        request_body[key] = value
    return request_body

def schedule_event(calendar_group_id, calendar_id, start_time, end_time, users_name):
    """Uses Outlook's Graph api to schedule an event based off the information provided
    
        Keyword arguments:\n
        start_time       -- The start time for the reservation\n
        end_time         -- The end time for the reservation

    """
    event_name = f"Reservation for {users_name}"
    body = {
        'contentType' : 'text',
        'content' : f'Reservation for {users_name}'
    }
    start = {
        'dateTime' : start_time,
        'timeZone' : 'America/Denver'
    }
    end = {
        'dateTime' : end_time,
        'timeZone' : 'America/Denver'
    }
    attendees = [
        {
            'emailAddress' : {
                'address' : f'{API.User.get_users_email()}'
            },
            'type' : 'required'
        }
    ]
    time_right_now = strftime('%Y-%m-%dT%H:%M:%S')
    if (start_time < time_right_now or end_time < time_right_now):
        return {"ERROR" : "Error : event was made in the past"}
    else:
        try:
            requests.post(
                API.graphAPI.GRAPH_API_ENDPOINT + f'/me/calendarGroups/{calendar_group_id}/calendars/{calendar_id}/events',
                headers=generate_headers(),
                json=construct_event_detail(
                    event_name,
                    body=body,
                    start=start,
                    end=end,
                    attendees=attendees,
                )
            )
            return {"SUCCESS" : "Successfully created an event"}
        except:
            return {"ERROR" : "Something went wrong with scheduling the event"}


def list_specific_calendar_in_group_events(calendar_group_id, calendar_id):
    """Uses the outlook api to get the events of a specific calendar in a calendar group and returns the events happening that day in an object with only the information needed. NOTE: events variable has all of the calendar information and I use a portion of the information found in events\n    

        Keyword arguments:\n
        calendar_group_id         -- The calendar group id that the calendar is located in
        calendar_id              -- The specific id for the calendar
    """

    calendar_headers = generate_headers()
    calendar_headers['Prefer'] = 'outlook.timezone="America/Denver"'

    start_date_time = strftime("%Y-%m-%dT%H:%M:%S")
    end_date_time = strftime("%Y-%m-%dT23:59:59")
    events = requests.get(
        API.graphAPI.GRAPH_API_ENDPOINT + f'/me/calendarGroups/{calendar_group_id}/calendars/{calendar_id}/calendarview?startdatetime={start_date_time}-06:00&endDateTime={end_date_time}-06:00',
        headers=calendar_headers
    )
    # To be returned for slack bot
    calendar_events = {}
    i = 0
    for event in events.json()['value']:
        eventDict = {}
        eventDict['webLink'] = event['webLink']
        eventDict['start'] = event['start']
        eventDict['end'] = event['end']
        calendar_events[f'event{i}'] = eventDict
        i += 1
    return calendar_events

def pretty_print_events(events, vehicle_name):
    """Makes the event object easier to read\n
    
        Keyword arguments:\n
        events      -- And object containing all of the events of a calendar\n
        vehicle_name -- The vehicle name the user inputed\n
    """
    if events == {}:
        message = f"There are no reservations for {vehicle_name}"
    else:            
        message = f'Reservations for {vehicle_name}\n'
        for i in range(len(events)):
            start_time = events[f"event{i}"]["start"]["dateTime"]
            cleaned_up_start_time = start_time.split('.')[0].split('T')[1][:-3] # Gets rid of microseconds, seconds and date
            cleaned_up_start_time = datetime.datetime.strptime(f'{cleaned_up_start_time}', '%H:%M').strftime('%I:%M %p') # Converts from military time to standard time

            end_time = events[f"event{i}"]["end"]["dateTime"]
            cleaned_up_end_time = end_time.split('.')[0].split('T')[1][:-3] # Gets rid of microseconds, seconds and date
            cleaned_up_end_time = datetime.datetime.strptime(f'{cleaned_up_end_time}', '%H:%M').strftime('%I:%M %p') # Converts from military time to standard time

            message += f'Start Time :  Today at {cleaned_up_start_time}\n'
            message += f'End Time   :  Today at {cleaned_up_end_time}\n'
            message += f'Web Link   :  {events[f"event{i}"]["webLink"]}\n'
            message += '\n\n'
    return message

def check_if_reservation_available(calendar_group_id, calendar_id, start_time, end_time):
    """Returns true or false if there is a reservation between start_time and end_time

    Keyword arguments:\n
        calendar_group_id      -- The calendar group id for outlook
        calendar_id            -- The calendar id for outlook
        start_time             -- The start time of the check
        end_time               -- The end time of the check
    """
    calendar_headers = generate_headers()
    calendar_headers['Prefer'] = 'outlook.timezone="America/Denver"'
    events = requests.get(
        API.graphAPI.GRAPH_API_ENDPOINT + f'/me/calendarGroups/{calendar_group_id}/calendars/{calendar_id}/calendarView?startDateTime={start_time}-06:00&endDateTime={end_time}-06:00', # NOTE: offset is needed or else this won't work
        headers=calendar_headers
    )
    return events.json()['value'] == []