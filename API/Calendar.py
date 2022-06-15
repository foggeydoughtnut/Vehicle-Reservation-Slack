import requests
import os
from time import strftime
import datetime
from API.graphAPI import generateAccessToken, GRAPH_API_ENDPOINT, SCOPES
from API.User import getUsersName, getUsersEmail
from dotenv import load_dotenv
load_dotenv()

application_id = os.getenv('APPLICATION_ID')

access_token = generateAccessToken(application_id, SCOPES)
headers = {
    'Authorization': 'Bearer ' + access_token
}


def constructEventDetail(event_name, **event_details):
    """ Constructs a calendar event with the name and details given

        Keyword arguments:\n
        event_name      -- The calendar event's name\n
        event_details   -- The details for the event (startTime, endTime, description, attendees)
    """
    request_body = {
        'subject' : event_name
    }
    for key, value in event_details.items():
        request_body[key] = value
    return request_body

def scheduleEvent(calendarGroupId, calendarId, startTime, endTime):
    """Uses Outlook's Graph api to schedule an event based off the information provided
    
        Keyword arguments:\n
        startTime       -- The start time for the reservation\n
        endTime         -- The end time for the reservation

    """
    event_name = "Reserve Vehicle"
    body = {
        'contentType' : 'text',
        'content' : f'Vehicle Reservation for {getUsersName()}'
    }
    start = {
        'dateTime' : startTime,
        'timeZone' : 'America/Denver'
    }
    end = {
        'dateTime' : endTime,
        'timeZone' : 'America/Denver'
    }
    attendees = [
        {
            'emailAddress' : {
                'address' : f'{getUsersEmail()}'
            },
            'type' : 'required'
        }
    ]
    requests.post(
        GRAPH_API_ENDPOINT + f'/me/calendarGroups/{calendarGroupId}/calendars/{calendarId}/events',
        headers=headers,
        json=constructEventDetail(
            event_name,
            body=body,
            start=start,
            end=end,
            attendees=attendees,
        )
    )


def listSpecificCalendarInGroupEvents(calendarGroupId, calendarId):
    """Uses the outlook api to get the events of a specific calendar in a calendar group and returns the events in an object with only the information needed NOTE: events variable has all of the calendar information and I use a portion of the information found in events\n    

        Keyword arguments:\n
        calendarGroupId         -- The calendar group id that the calendar is located in
        calendarId              -- The specific id for the calendar
    """

    calendarHeaders = headers
    calendarHeaders['Prefer'] = 'outlook.timezone="America/Denver"'

    startDateTime = strftime("%Y-%m-%dT%H:%M:%S")
    endDateTime = strftime("%Y-%m-%d")+'T23:59'
    events = requests.get(
        GRAPH_API_ENDPOINT + f'/me/calendarGroups/{calendarGroupId}/calendars/{calendarId}/calendarView?startDateTime={startDateTime}&endDateTime={endDateTime}',
        headers=calendarHeaders
    )
    # To be returned for slack bot
    calendarEvents = {}
    i = 0
    for event in events.json()['value']:
        eventDict = {}
        eventDict[f'event'] = f'event{i}'
        eventDict['Subject'] = event['subject']
        eventDict['bodyPreview'] = event['bodyPreview']
        eventDict['webLink'] = event['webLink']
        eventDict['start'] = event['start']
        eventDict['end'] = event['end']
        calendarEvents[f'event{i}'] = eventDict
        i += 1
    
    return calendarEvents

def prettyPrintEvents(events, vehicleName):
    """Makes the event object easier to read\n
    
        Keyword arguments:\n
        events      -- And object containing all of the events of a calendar\n
        vehicleName -- The vehicle name the user inputed\n
    """
    if events == {}:
        message = f"There are no reservations for {vehicleName}"
    else:            
        message = f'{vehicleName}\'s calendar looks like this : \n'
        for i in range(len(events)):
            startTime = events[f"event{i}"]["start"]["dateTime"]
            # startTime = startTime.split('.')[0].replace('T', ' at ')
            cleandedUpStartTime = startTime.split('.')[0].split('T')[1][:-3] # Gets rid of microseconds, seconds and date

            cleandedUpStartTime = datetime.datetime.strptime(f'{cleandedUpStartTime}', '%H:%M').strftime('%I:%M %p')
            print(cleandedUpStartTime)

            endTime = events[f"event{i}"]["end"]["dateTime"]
            # endTime = endTime.split('.')[0].replace('T', ' at ')
            cleanedUpEndTime = endTime.split('.')[0].split('T')[1][:-3] # Gets rid of microseconds, seconds and date
            cleanedUpEndTime = datetime.datetime.strptime(f'{cleanedUpEndTime}', '%H:%M').strftime('%I:%M %p')

            message += f'Event         :  {events[f"event{i}"]["event"]}\n'
            message += f'Subject      :  {events[f"event{i}"]["Subject"]}\n'
            message += f'Body          :  {events[f"event{i}"]["bodyPreview"]}\n'
            message += f'Start Time :  Today at {cleandedUpStartTime}\n'
            message += f'End Time   :  Today at {cleanedUpEndTime}\n'
            message += f'Web Link   :  {events[f"event{i}"]["webLink"]}\n'
            message += '\n\n'
    return message


# #  Delete an event
# event_id1 = response1_create.json()['id'] # get event id then do a delete request
# response1_delete = requests.delete(
#     GRAPH_API_ENDPOINT + f'/me/events/{event_id1}',
#     headers=headers
# )
# print(response1_delete.status_code)

# # Cancel an event
# event_id1 = response1_create.json()['id'] # get event id then do a post request to the /cancel route
# response1_delete = requests.post(
#     GRAPH_API_ENDPOINT + f'/me/events/{event_id1}/cancel',
#     headers=headers
# )