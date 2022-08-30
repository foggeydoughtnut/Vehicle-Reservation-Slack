from time import strftime
import api.Calendar
import api.graph_api
from time import strftime
from datetime import datetime, timedelta
import json


def test_generate_headers():
    headers = api.Calendar.generate_headers()
    assert api.Calendar.generate_headers()
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
    event_details = api.Calendar.construct_event_detail(
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

    status = api.Calendar.schedule_event('', '', start, end, '')

    assert status["SUCCESS"]
    assert type(status) == dict

def test_schedule_event_fails_past():
    """Tests if schedule_event returns ERROR when event is made in the past"""
    status = api.Calendar.schedule_event('', '', '2022-06-27T08:00:00', '2022-06-27T08:30:00', '')
    assert type(status) == dict
    assert status["ERROR"]

def test_schedule_event_fails_no_time():
    """Tests if Error is returned when no start/end time is given"""
    status = api.Calendar.schedule_event('', '', '', '', '')
    assert type(status) == dict
    assert status["ERROR"]

def test_list_specific_calendar_events(requests_mock, mocker):
    test_calendar_group_id = 'calendar_group_id'
    test_calendar_id = 'calendar_id'
    start_date_time = strftime("%Y-%m-%dT%H:%M:%S")
    end_date_time = strftime("%Y-%m-%dT23:59:59")
    mocker.patch('api.Calendar.generate_headers', return_value={'test': 'testing'})
    requests_mock.get(
        f"{api.graph_api.GRAPH_API_ENDPOINT}/me/calendarGroups/{test_calendar_group_id}/calendars/{test_calendar_id}/calendarview?startdatetime={start_date_time}-06:00&endDateTime={end_date_time}-06:00",
        json = {'value' : [
            {
                'webLink' : 'test link',
                'start' : '2022-06-27T12:00:00',
                'end' : '2022-06-27T13:00:00',
            }
        ]
        },
        status_code=200,
    )
    resp = api.Calendar.list_specific_calendar_in_group_events(test_calendar_group_id, test_calendar_id)
    assert type(resp) == dict
    assert resp['event0']['webLink'] == 'test link'
    assert resp['event0']['start'] == '2022-06-27T12:00:00'
    assert resp['event0']['end'] == '2022-06-27T13:00:00'

def test_check_if_reservation_available(requests_mock, mocker):
    test_calendar_group_id = 'calendar_group_id'
    test_calendar_id = 'calendar_id'
    s_time = strftime("%Y-%m-%dT%H:%M")
    offset_minutes = 15 # 15 Minute offset for check availability
    offset_time = datetime.strptime(s_time, '%Y-%m-%dT%H:%M') + timedelta(minutes=offset_minutes)
    e_time = offset_time.strftime('%Y-%m-%dT%H:%M')
    # offset needed for correct mock url
    s_time_offset = datetime.strptime(s_time, '%Y-%m-%dT%H:%M') + timedelta(minutes=1)
    e_time_offset = datetime.strptime(e_time, '%Y-%m-%dT%H:%M') - timedelta(minutes=1)
    s_time_offset_formatted = s_time_offset.strftime('%Y-%m-%dT%H:%M')
    e_time_offset_formatted = e_time_offset.strftime('%Y-%m-%dT%H:%M')
    ####
    mocker.patch('api.Calendar.generate_headers', return_value={'test': 'testing'})
    requests_mock.get(
        f"{api.graph_api.GRAPH_API_ENDPOINT}/me/calendarGroups/{test_calendar_group_id}/calendars/{test_calendar_id}/calendarview?startDateTime={s_time_offset_formatted}-06:00&endDateTime={e_time_offset_formatted}-06:00",
        json = {'value' : []},
        status_code=200,
    )
    resp = api.Calendar.check_if_reservation_available(test_calendar_group_id, test_calendar_id, s_time, e_time)
    assert resp == True
    assert type(resp) == bool

def test_available_fails_if_event(requests_mock, mocker):
    """Checks that it returns false if there is an event in the time"""
    test_calendar_group_id = 'calendar_group_id'
    test_calendar_id = 'calendar_id'
    s_time = strftime("%Y-%m-%dT%H:%M")
    offset_minutes = 15 # 15 Minute offset for check availability
    offset_time = datetime.strptime(s_time, '%Y-%m-%dT%H:%M') + timedelta(minutes=offset_minutes)
    e_time = offset_time.strftime('%Y-%m-%dT%H:%M')

    s_time_offset = datetime.strptime(s_time, '%Y-%m-%dT%H:%M') + timedelta(minutes=1)
    e_time_offset = datetime.strptime(e_time, '%Y-%m-%dT%H:%M') - timedelta(minutes=1)
    s_time_offset_formatted = s_time_offset.strftime('%Y-%m-%dT%H:%M')
    e_time_offset_formatted = e_time_offset.strftime('%Y-%m-%dT%H:%M')

    mocker.patch('api.Calendar.generate_headers', return_value={'test': 'testing'})
    requests_mock.get(
        f"{api.graph_api.GRAPH_API_ENDPOINT}/me/calendarGroups/{test_calendar_group_id}/calendars/{test_calendar_id}/calendarview?startdatetime={s_time_offset_formatted}-06:00&endDateTime={e_time_offset_formatted}-06:00",
        json = {'value' : [
            {
                'webLink' : 'test link',
                'start' : '2022-06-27T12:00:00',
                'end' : '2022-06-27T13:00:00',
            }
        ]},
        status_code=200,
    )
    resp = api.Calendar.check_if_reservation_available(test_calendar_group_id, test_calendar_id, s_time, e_time)
    assert resp == False
    assert type(resp) == bool

def test_construct_calendar_events_block():
    test_events = {
        'event0': {
            'webLink': 'https://www.google.com/',
            'start': {
                'dateTime': '2022-08-08T10:00:00.0000000',
                'timeZone': 'America/Denver'
            },
            'end': {
                'dateTime': '2022-08-08T11:00:00.0000000',
                'timeZone': 'America/Denver'
            }
        }
    }
    # reservations_results.json should look like this
    reservations_results_json_file_ex = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Reservations for test"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Start Time :* Today at 10:00 AM"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*End Time   : * Today at 11:00 AM"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Web Link   : * <https://www.google.com/|Link to the Calendar Event>"
                }
            },
            {
                "type": "divider"
            }
        ]
    }
    res = api.Calendar.construct_calendar_events_block(test_events, 'test')
    with open('app/slack_blocks/reservations_results.json', 'r') as f:
        data = json.load(f)
    assert res['reservations'] == True
    # See https://stackoverflow.com/questions/46914222/how-can-i-assert-lists-equality-with-pytest
    assert len(data) == len(reservations_results_json_file_ex)
    assert all([a == b for a, b in zip(data, reservations_results_json_file_ex)])


def test_construct_calendar_events_block_no_events():
    res = api.Calendar.construct_calendar_events_block({}, 'test')
    assert res['reservations'] == False