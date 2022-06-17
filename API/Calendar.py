import requests
import os
from time import strftime
import datetime
import API.graphAPI
import API.User
from dotenv import load_dotenv
load_dotenv()


application_id = os.getenv('APPLICATION_ID')


def generateHeaders():
    access_token = API.graphAPI.generateAccessToken(application_id, API.graphAPI.SCOPES)
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    return headers


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
        'content' : f'Vehicle Reservation for {API.User.getUsersName()}'
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
                'address' : f'{API.User.getUsersEmail()}'
            },
            'type' : 'required'
        }
    ]
    requests.post(
        API.graphAPI.GRAPH_API_ENDPOINT + f'/me/calendarGroups/{calendarGroupId}/calendars/{calendarId}/events',
        headers=generateHeaders(),
        json=constructEventDetail(
            event_name,
            body=body,
            start=start,
            end=end,
            attendees=attendees,
        )
    )


def listSpecificCalendarInGroupEvents(calendarGroupId, calendarId):
    """Uses the outlook api to get the events of a specific calendar in a calendar group and returns the events happening that day in an object with only the information needed. NOTE: events variable has all of the calendar information and I use a portion of the information found in events\n    

        Keyword arguments:\n
        calendarGroupId         -- The calendar group id that the calendar is located in
        calendarId              -- The specific id for the calendar
    """

    calendarHeaders = generateHeaders()
    calendarHeaders['Prefer'] = 'outlook.timezone="America/Denver"'

    startDateTime = strftime("%Y-%m-%dT%H:%M:%S")
    endDateTime = strftime("%Y-%m-%dT23:59:59")
    events = requests.get(
        API.graphAPI.GRAPH_API_ENDPOINT + f'/me/calendarGroups/{calendarGroupId}/calendars/{calendarId}/calendarview?startdatetime={startDateTime}-06:00&endDateTime={endDateTime}-06:00',
        headers=calendarHeaders
    )

    # events = requests.get(
    #     API.graphAPI.GRAPH_API_ENDPOINT + f'/me/calendarview?startdatetime={startDateTime}&endDateTime={endDateTime}',
    #     headers=calendarHeaders
    # )
    # print(events)

    # events = requests.get( 
    #     API.graphAPI.GRAPH_API_ENDPOINT + f'/me/calendarGroups/{calendarGroupId}/calendars/{calendarId}/events',
    #     headers=calendarHeaders
    # )

    # To be returned for slack bot
    calendarEvents = {}
    i = 0
    for event in events.json()['value']:
        eventDict = {}
        eventDict['event'] = f'event{i}'
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
            cleandedUpStartTime = startTime.split('.')[0].split('T')[1][:-3] # Gets rid of microseconds, seconds and date

            cleandedUpStartTime = datetime.datetime.strptime(f'{cleandedUpStartTime}', '%H:%M').strftime('%I:%M %p') # Converts from military time to standard time

            endTime = events[f"event{i}"]["end"]["dateTime"]
            cleanedUpEndTime = endTime.split('.')[0].split('T')[1][:-3] # Gets rid of microseconds, seconds and date
            cleanedUpEndTime = datetime.datetime.strptime(f'{cleanedUpEndTime}', '%H:%M').strftime('%I:%M %p') # Converts from military time to standard time

            message += f'Event         :  {events[f"event{i}"]["event"]}\n'
            message += f'Subject      :  {events[f"event{i}"]["Subject"]}\n'
            message += f'Body          :  {events[f"event{i}"]["bodyPreview"]}\n'
            message += f'Start Time :  Today at {cleandedUpStartTime}\n'
            message += f'End Time   :  Today at {cleanedUpEndTime}\n'
            message += f'Web Link   :  {events[f"event{i}"]["webLink"]}\n'
            message += '\n\n'
    return message

def checkIfReservationAvailable(calendarGroupId, calendarId, startTime, endTime):
    calendarHeaders = generateHeaders()
    calendarHeaders['Prefer'] = 'outlook.timezone="America/Denver"'
    events = requests.get(
        API.graphAPI.GRAPH_API_ENDPOINT + f'/me/calendarGroups/{calendarGroupId}/calendars/{calendarId}/calendarView?startDateTime={startTime}-06:00&endDateTime={endTime}-06:00', # NOTE: offset is needed or else this won't work
        headers=calendarHeaders
    )
    return events.json()['value'] == []


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