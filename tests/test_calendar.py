from time import strftime
import API.Calendar
import API.graphAPI
from time import strftime
from datetime import datetime, timedelta


def test_generate_headers():
    headers = API.Calendar.generate_headers()
    assert API.Calendar.generate_headers()
    assert type(headers) == dict
    assert headers["Authorization"]

def test_construct_event_details():
    event_name = "Reserve Vehicle"
    body = {
        'contentType' : 'text',
        'content' : 'Vehicle Reservation for test@email.com'
    }
    start = {
        'dateTime' : 'test start time',
        'timeZone' : 'America/Denver'
    }
    end = {
        'dateTime' : 'test end time',
        'timeZone' : 'America/Denver'
    }
    attendees = [
        {
            'emailAddress' : {
                'address' : 'test@email.com'
            },
            'type' : 'required'
        }
    ]
    event_details = API.Calendar.construct_event_detail(
        event_name,
        body=body,
        start=start,
        end=end,
        attendees=attendees,
    )
    assert type(event_details) == dict
    assert event_details['subject'] == 'Reserve Vehicle'
    assert event_details['body'] == {'contentType': 'text', 'content': 'Vehicle Reservation for test@email.com'}
    assert event_details['start'] == {'dateTime': 'test start time', 'timeZone': 'America/Denver'}
    assert event_details['end'] == {'dateTime': 'test end time', 'timeZone': 'America/Denver'}
    
def test_schedule_event():
    start_time = strftime("%Y-%m-%dT%H:%M:%S")
    offset_start_minutes = 15 # 15 Minute offset for check availability
    offset_end_minutes = 60
    offset_start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S') + timedelta(minutes=offset_start_minutes)
    offset_end_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S') + timedelta(minutes=offset_end_minutes)
    start = offset_start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end = offset_end_time.strftime('%Y-%m-%dT%H:%M:%S')

    status = API.Calendar.schedule_event('', '', start, end)

    assert status["SUCCESS"]
    assert type(status) == dict

def test_schedule_event_fails_past():
    """Tests if schedule_event returns ERROR when event is made in the past"""
    status = API.Calendar.schedule_event('', '', '2022-06-27T08:00:00', '2022-06-27T08:30:00')
    assert type(status) == dict
    assert status["ERROR"]

def test_schedule_event_fails_no_time():
    """Tests if Error is returned when no start/end time is given"""
    status = API.Calendar.schedule_event('', '', '', '')
    assert type(status) == dict
    assert status["ERROR"]

def test_list_specific_calendar_events(requests_mock, mocker):
    test_calendar_group_id = 'calendar_group_id'
    test_calendar_id = 'calendar_id'
    start_date_time = strftime("%Y-%m-%dT%H:%M:%S")
    end_date_time = strftime("%Y-%m-%dT23:59:59")
    mocker.patch('API.Calendar.generate_headers', return_value={'test': 'testing'})
    requests_mock.get(
        f"{API.graphAPI.GRAPH_API_ENDPOINT}/me/calendarGroups/{test_calendar_group_id}/calendars/{test_calendar_id}/calendarview?startdatetime={start_date_time}-06:00&endDateTime={end_date_time}-06:00",
        json = {'value' : [
            {
                'subject' : 'test',
                'bodyPreview' : 'test event',
                'webLink' : 'test link',
                'start' : '2022-06-27T12:00:00',
                'end' : '2022-06-27T13:00:00',
            }
        ]
        },
        status_code=200,
    )
    resp = API.Calendar.list_specific_calendar_in_group_events(test_calendar_group_id, test_calendar_id)
    assert type(resp) == dict
    assert resp['event0']['event'] == 'event0'
    assert resp['event0']['Subject'] == 'test'
    assert resp['event0']['bodyPreview'] == 'test event'
    assert resp['event0']['webLink'] == 'test link'
    assert resp['event0']['start'] == '2022-06-27T12:00:00'
    assert resp['event0']['end'] == '2022-06-27T13:00:00'

def test_check_if_reservation_available(requests_mock, mocker):
    test_calendar_group_id = 'calendar_group_id'
    test_calendar_id = 'calendar_id'
    start_time = strftime("%Y-%m-%dT%H:%M:%S")
    offset_minutes = 15 # 15 Minute offset for check availability
    offset_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S') + timedelta(minutes=offset_minutes)
    end_time = offset_time.strftime('%Y-%m-%dT%H:%M:%S')
    mocker.patch('API.Calendar.generate_headers', return_value={'test': 'testing'})
    requests_mock.get(
        f"{API.graphAPI.GRAPH_API_ENDPOINT}/me/calendarGroups/{test_calendar_group_id}/calendars/{test_calendar_id}/calendarview?startdatetime={start_time}-06:00&endDateTime={end_time}-06:00",
        json = {'value' : []},
        status_code=200,
    )
    resp = API.Calendar.check_if_reservation_available(test_calendar_group_id, test_calendar_id, start_time, end_time)
    assert resp == True
    assert type(resp) == bool

def test_available_fails_if_event(requests_mock, mocker):
    """Checks that it returns false if there is an event in the time"""
    test_calendar_group_id = 'calendar_group_id'
    test_calendar_id = 'calendar_id'
    start_time = strftime("%Y-%m-%dT%H:%M:%S")
    offset_minutes = 15 # 15 Minute offset for check availability
    offset_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S') + timedelta(minutes=offset_minutes)
    end_time = offset_time.strftime('%Y-%m-%dT%H:%M:%S')
    mocker.patch('API.Calendar.generate_headers', return_value={'test': 'testing'})
    requests_mock.get(
        f"{API.graphAPI.GRAPH_API_ENDPOINT}/me/calendarGroups/{test_calendar_group_id}/calendars/{test_calendar_id}/calendarview?startdatetime={start_time}-06:00&endDateTime={end_time}-06:00",
        json = {'value' : [
            {
                'subject' : 'test',
                'bodyPreview' : 'test event',
                'webLink' : 'test link',
                'start' : '2022-06-27T12:00:00',
                'end' : '2022-06-27T13:00:00',
            }
        ]},
        status_code=200,
    )
    resp = API.Calendar.check_if_reservation_available(test_calendar_group_id, test_calendar_id, start_time, end_time)
    assert resp == False
    assert type(resp) == bool


def test_pretty_print_events_return_message_empty():
    """Tests that pretty_print_events returns that there are no reservations when events is empty"""
    message = API.Calendar.pretty_print_events({}, 'test')
    assert message == "There are no reservations for test"

def test_pretty_print_events():
    message = API.Calendar.pretty_print_events({'event0': {
        'event' : 'test event',
        'Subject' : 'test subject',
        'bodyPreview' : 'test body preview',
        'webLink' : 'test web link',
        'start' : {'dateTime' : '2022-06-27T14:30:00'},
        'end' : {'dateTime' : '2022-06-27T15:00:00'},
    }}, 'test')
    test_message = "test's calendar looks like this : \n"
    test_message += 'Event         :  test event\n'
    test_message += 'Subject      :  test subject\n'
    test_message += 'Body          :  test body preview\n'
    test_message += 'Start Time :  Today at 02:30 PM\n'
    test_message += 'End Time   :  Today at 03:00 PM\n'
    test_message += 'Web Link   :  test web link\n'
    test_message += '\n\n'
    assert message == test_message
