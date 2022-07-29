from app import get_selected_vehicle_name_from_payload, get_start_end_time_from_payload, check_available, reserve_vehicle, check_vehicle, get_reservations

import API.db.index
import API.Calendar
import pytest


test_payload = {
    "type": "block_actions",
    "user": {
        "id": "test_user_id",
        "username": "test_user_name",
        "name": "test_user_name",
        "team_id": "test_team_id"
    },
    "api_app_id": "test_api_app_id",
    "token": "test_token",
    "container": {
        "type": "message",
        "message_ts": "test_message_ts",
        "channel_id": "test_channel_id",
        "is_ephemeral": False,
        "thread_ts": "test_thread_ts"
    },
    "trigger_id": "3766018397026.3586337590197.b57e6ad64d73ac0867d7c63b4df0549a",
    "team": {
        "id": "test_team_id",
        "domain": "test_domain"
    },
    "enterprise": '',
    "is_enterprise_install": False,
    "channel": {
        "id": "test_channel_id",
        "name": "reserving-vehicles"
    },
    "message": {
        "bot_id": "test_bot_id",
        "type": "message",
        "text": "Please fill out the form",
        "user": "test_user",
        "ts": "test_message_ts",
        "app_id": "test_api_app_id",
        "team": "test_team_id",
        "blocks": [
            {
                "type": "header",
                "block_id": "9Xe",
                "text": {
                    "type": "plain_text",
                    "text": "Reserve",
                    "emoji": True
                }
            },
            {
                "type": "input",
                "block_id": "=c6fL",
                "label": {
                    "type": "plain_text",
                    "text": "Choose a Vehicle",
                    "emoji": True
                },
                "optional": False,
                "dispatch_action": False,
                "element": {
                    "type": "static_select",
                    "action_id": "static_select-action",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a vehicle",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "test1",
                                "emoji": True
                            },
                            "value": "value-0"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "test2",
                                "emoji": True
                            },
                            "value": "value-1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "test3",
                                "emoji": True
                            },
                            "value": "value-2"
                        }
                    ]
                }
            },
            {
                "type": "input",
                "block_id": "Li5e",
                "label": {
                    "type": "plain_text",
                    "text": "Start Date",
                    "emoji": True
                },
                "optional": False,
                "dispatch_action": False,
                "element": {
                    "type": "datepicker",
                    "action_id": "datepicker-action",
                    "initial_date": "2022-07-01",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a date",
                        "emoji": True
                    }
                }
            },
            {
                "type": "input",
                "block_id": "tqe",
                "label": {
                    "type": "plain_text",
                    "text": "Start Time",
                    "emoji": True
                },
                "optional": False,
                "dispatch_action": False,
                "element": {
                    "type": "timepicker",
                    "action_id": "timepicker-action",
                    "initial_time": "13:00",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select time",
                        "emoji": True
                    }
                }
            },
            {
                "type": "divider",
                "block_id": "vae"
            },
            {
                "type": "input",
                "block_id": "I45",
                "label": {
                    "type": "plain_text",
                    "text": "End Date",
                    "emoji": True
                },
                "optional": False,
                "dispatch_action": False,
                "element": {
                    "type": "datepicker",
                    "action_id": "datepicker-action",
                    "initial_date": "2022-07-01",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a date",
                        "emoji": True
                    }
                }
            },
            {
                "type": "input",
                "block_id": "27J",
                "label": {
                    "type": "plain_text",
                    "text": "End Time",
                    "emoji": True
                },
                "optional": False,
                "dispatch_action": False,
                "element": {
                    "type": "timepicker",
                    "action_id": "timepicker-action",
                    "initial_time": "14:00",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select time",
                        "emoji": True
                    }
                }
            },
            {
                "type": "actions",
                "block_id": "tVc",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "submit",
                        "text": {
                            "type": "plain_text",
                            "text": "Reserve",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "confirm": {
                            "title": {
                                "type": "plain_text",
                                "text": "Are you sure?",
                                "emoji": True
                            },
                            "text": {
                                "type": "mrkdwn",
                                "text": "button text smaller description",
                                "verbatim": False
                            },
                            "confirm": {
                                "type": "plain_text",
                                "text": "Do it",
                                "emoji": True
                            },
                            "deny": {
                                "type": "plain_text",
                                "text": "Stop, I've changed my mind!",
                                "emoji": True
                            }
                        }
                    }
                ]
            }
        ],
        "thread_ts": "test_thread_ts",
        "parent_user_id": "test_user_id"
    },
    "state": {
        "values": {
            "=c6fL": {
                "static_select-action": {
                    "type": "static_select",
                    "selected_option": {
                        "text": {
                            "type": "plain_text",
                            "text": "test1",
                            "emoji": True
                        },
                        "value": "value-0"
                    }
                }
            },
            "Li5e": {
                "datepicker-action": {
                    "type": "datepicker",
                    "selected_date": "2022-07-07"
                }
            },
            "tqe": {
                "timepicker-action": {
                    "type": "timepicker",
                    "selected_time": "13:00"
                }
            },
            "I45": {
                "datepicker-action": {
                    "type": "datepicker",
                    "selected_date": "2022-07-07"
                }
            },
            "27J": {
                "timepicker-action": {
                    "type": "timepicker",
                    "selected_time": "14:00"
                }
            },
            "9N2": {
                "plain_text_input-action": {
                    "type": "plain_text_input",
                    "value": "test"
                }
            }
        }
    },
    "response_url": "https://hooks.slack.com/actions/test_team_id/3778669912369/6v0ZuREA1deM6VMGGEHr0qhp",
    "actions": [
        {
            "confirm": {
                "title": {
                    "type": "plain_text",
                    "text": "Are you sure?",
                    "emoji": True
                },
                "text": {
                    "type": "mrkdwn",
                    "text": "button text smaller description",
                    "verbatim": False
                },
                "confirm": {
                    "type": "plain_text",
                    "text": "Do it",
                    "emoji": True
                },
                "deny": {
                    "type": "plain_text",
                    "text": "Stop, I've changed my mind!",
                    "emoji": True
                }
            },
            "action_id": "submit",
            "block_id": "tVc",
            "text": {
                "type": "plain_text",
                "text": "Reserve",
                "emoji": True
            },
            "value": "click_me_123",
            "type": "button",
            "action_ts": "1657122470.963155"
        }
    ]
}

def test_get_selected_vehicle_name_from_payload():
    vehicle_name = get_selected_vehicle_name_from_payload(test_payload)
    assert vehicle_name == 'test1'

def test_start_end_time_from_payload():
    start, end = get_start_end_time_from_payload(test_payload)
    assert start == '2022-07-07T13:00'
    assert end == '2022-07-07T14:00'

class Vehicle:
    name = 'test_name'
    calendarGroupID = 'test_calendar_group_id'
    calendarID = 'test_calendar_id'

def test_check_available(mocker):
    mocker.patch('API.Calendar.check_if_reservation_available', return_value=True)
    vehicle = Vehicle()
    available = check_available(vehicle, 'start_time', 'end_time')
    assert available == True

def test_reserve_vehicle_successfull(mocker):
    mocker.patch('API.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch('app.check_available', return_value=True)
    mocker.patch('API.Calendar.schedule_event', return_value={"SUCCESS" : "Successfully created an event"})
    mocker.patch('app.send_message', return_value='SUCCESS')
    res = reserve_vehicle(test_payload, 'test')
    assert res['status'] == 200

def test_reserve_vehicle_error_schedule(mocker):
    """Returns a 500 error when API.Calendar.schedule_event returns an error"""
    mocker.patch('API.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch('app.check_available', return_value=True)
    mocker.patch('API.Calendar.schedule_event', return_value={"ERROR" : "An error occured"})
    mocker.patch('app.send_message', return_value='')
    res = reserve_vehicle(test_payload, 'test')
    assert res['status'] == 500

def test_reserve_vehicle_not_available(mocker):
    """Returns a 400 status if the vehicle is not available"""
    mocker.patch('API.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch('app.check_available', return_value=False)
    mocker.patch('app.send_message', return_value='')
    res = reserve_vehicle(test_payload, 'test')
    assert res['status'] == 400

def test_reserve_vehicle_exception(mocker):
    """Returns status of 500 when exception occurs"""
    mocker.patch('API.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch('app.check_available', side_effect=Exception("mocked error"))
    mocker.patch('app.send_message', return_value='')
    res = reserve_vehicle(test_payload, 'test')
    assert res['status'] == 500


def test_check_vehicle_success(mocker):
    mocker.patch('API.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch('app.check_available', return_value=True)
    mocker.patch('app.send_message', return_value='')
    res = check_vehicle(test_payload, 'test')
    assert res['status'] == 200

def test_check_vehicle_unavailable(mocker):
    mocker.patch('API.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch('app.check_available', return_value=False)
    mocker.patch('app.send_message', return_value='')
    res = check_vehicle(test_payload, 'test')
    assert res['status'] == 400

def test_check_vehicle_exception(mocker):
    mocker.patch('API.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch('app.check_available', side_effect=Exception('mocked exception'))
    mocker.patch('app.send_message', return_value='')
    res = check_vehicle(test_payload, 'test')
    assert res['status'] == 500


def test_get_reservations(mocker):
    """Returns a status of 200 when no exceptions occur NOTE only checking
    because API.calendar already checked that list_specific_calendar_in_group_events worked
    """
    mocker.patch('API.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch('API.Calendar.list_specific_calendar_in_group_events', return_value={})
    mocker.patch('API.Calendar.pretty_print_events', return_value={})
    mocker.patch('app.send_message', return_value='')
    res = get_reservations(test_payload, 'test')
    assert res['status'] == 200

def test_get_reservations_excpetion(mocker):
    """Tests that 500 status is returned when exception occurs"""
    mocker.patch('API.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch('API.Calendar.list_specific_calendar_in_group_events', side_effect=Exception('mocked exception'))
    mocker.patch('app.send_message', return_value='')
    res = get_reservations(test_payload, 'test')
    assert res['status'] == 500