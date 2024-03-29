import requests
import os
import json
from datetime import datetime, timedelta
import api.graph_api
from dotenv import load_dotenv
from time import strftime
load_dotenv()


application_id = os.getenv('APPLICATION_ID')


def generate_headers(user_slack_id):
    access_token = api.graph_api.generate_access_token(application_id, api.graph_api.SCOPES, user_slack_id)
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
        'subject': event_name
    }
    for key, value in event_details.items():
        request_body[key] = value
    return request_body


def schedule_event(calendar_group_id, calendar_id, start_time, end_time, users_name, user_id):
    """Uses Outlook's Graph api to schedule an event based off the information provided
    
        Keyword arguments:\n
        start_time       -- The start time for the reservation\n
        end_time         -- The end time for the reservation\n
        users_name       -- The name for the reserve\n
        user_id          -- The user's Slack id
    """
    event_name = f"Reservation for {users_name}"
    body = {
        'contentType': 'text',
        'content': f'Reservation for {users_name}'
    }
    start = {
        'dateTime': start_time,
        'timeZone': 'America/Denver'
    }
    end = {
        'dateTime': end_time,
        'timeZone': 'America/Denver'
    }
    time_right_now = strftime('%Y-%m-%dT%H:%M:%S')
    if start_time < time_right_now or end_time < time_right_now:
        return {"ERROR": "Error : event was made in the past"}
    else:
        try:
            requests.post(
                api.graph_api.GRAPH_API_ENDPOINT + f'/me/calendarGroups/{calendar_group_id}'
                                                   f'/calendars/{calendar_id}/events',
                headers=generate_headers(user_id),
                json=construct_event_detail(
                    event_name,
                    body=body,
                    start=start,
                    end=end,
                )
            )
            return {"SUCCESS": "Successfully created an event"}
        except:
            return {"ERROR": "Something went wrong with scheduling the event"}


def list_specific_calendar_in_group_events(calendar_group_id, calendar_id, user_id):
    """Uses the outlook api to get the events of a specific calendar in a calendar group and returns the events
    happening that day in an object with only the information needed. NOTE: events variable has all the calendar
    information and I use a portion of the information found in events\n

        Keyword arguments:\n
        calendar_group_id         -- The calendar group id that the calendar is located in\n
        calendar_id               -- The specific id for the calendar\n 
        user_id                   -- The user's Slack id
    """

    calendar_headers = generate_headers(user_id)
    calendar_headers['Prefer'] = 'outlook.timezone="America/Denver"'

    start_date_time = strftime("%Y-%m-%dT%H:%M:%S")
    end_date_time = strftime("%Y-%m-%dT23:59:59")
    events = requests.get(
        api.graph_api.GRAPH_API_ENDPOINT + f'/me/calendarGroups/{calendar_group_id}/calendars/{calendar_id}'
                                           f'/calendarview?startdatetime={start_date_time}-06:00'
                                           f'&endDateTime={end_date_time}-06:00',
        headers=calendar_headers
    )
    # To be returned for slack bot
    calendar_events = {}
    i = 0
    for event in events.json()['value']:
        event_dict = {
            'webLink': event['webLink'],
            'start': event['start'],
            'end': event['end']
        }
        calendar_events[f'event{i}'] = event_dict
        i += 1
    return calendar_events


def construct_calendar_events_block(events, vehicle_name):
    """Uses the events passed in to create the calendar events slack block used by the reservations command\n

        Keyword Arguments:\n
        events       -- The events on the calendar found by the outlook api\n
        vehicle_name -- The vehicle name that was selected
    """
    if events == {}:
        return {'reservations': False}
    else:
        with open("app/slack_blocks/reservations_results.json", "r+") as f:
            f.truncate(0)  # Clear the json file
        reservations_dict = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"Reservations for {vehicle_name}",
                    }
                },
                {
                    "type": "divider"
                },
            ]
        }
        for i in range(len(events)):
            start_time = events[f"event{i}"]["start"]["dateTime"]
            cleaned_up_start_time = start_time.split('.')[0].split('T')[1][
                                    :-3]  # Gets rid of microseconds, seconds and date
            cleaned_up_start_time = datetime.strptime(f'{cleaned_up_start_time}', '%H:%M').strftime(
                '%I:%M %p')  # Converts from military time to standard time

            end_time = events[f"event{i}"]["end"]["dateTime"]
            cleaned_up_end_time = end_time.split('.')[0].split('T')[1][
                                  :-3]  # Gets rid of microseconds, seconds and date
            cleaned_up_end_time = datetime.strptime(f'{cleaned_up_end_time}', '%H:%M').strftime(
                '%I:%M %p')  # Converts from military time to standard time

            url_to_event = events[f"event{i}"]['webLink']
            reservations_dict['blocks'].extend([
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Start Time :* Today at {cleaned_up_start_time}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*End Time   : * Today at {cleaned_up_end_time}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Web Link   : * <{url_to_event}|Link to the Calendar Event>"
                    }
                },
                {
                    "type": "divider"
                },
            ])
            json_string = json.dumps(reservations_dict)
            with open("app/slack_blocks/reservations_results.json", "w") as f:
                f.write(json_string)
        return {'reservations': True}


def check_if_reservation_available(calendar_group_id, calendar_id, start_time, end_time, user_id):
    """Returns true or false if there is a reservation between start_time and end_time

    Keyword arguments:\n
        calendar_group_id      -- The calendar group id for Outlook\n
        calendar_id            -- The calendar id for outlook\n
        start_time             -- The start time of the check\n
        end_time               -- The end time of the check\n
        user_id                -- The user's Slack id
    """
    # Offset start time and end time by one minute to allow reservations like 9-10 and 10-11 to happen.
    start_offset_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M') + timedelta(minutes=1)
    s_time = start_offset_time.strftime('%Y-%m-%dT%H:%M')
    end_offset_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M') - timedelta(minutes=1)
    e_time = end_offset_time.strftime('%Y-%m-%dT%H:%M')

    calendar_headers = generate_headers(user_id)
    calendar_headers['Prefer'] = 'outlook.timezone="America/Denver"'
    events = requests.get(
        api.graph_api.GRAPH_API_ENDPOINT + f'/me/calendarGroups/{calendar_group_id}/calendars/{calendar_id}'
                                           f'/calendarView?startDateTime={s_time}-06:00&endDateTime={e_time}-06:00',
        # NOTE: offset is needed or else this won't work
        headers=calendar_headers
    )
    return events.json()['value'] == []
