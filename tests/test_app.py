from app import app as test_app, get_selected_vehicle_name_from_payload, get_start_end_time_from_payload
import API.db.index
import pytest

@pytest.fixture()
def app():
    test_app.config.update({
        "TESTING": True,
    })
    yield test_app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_login(client):
    # create test admin user to log in
    test_user = API.db.index.get_user_by_username('test-user')
    if (test_user):
        API.db.index.delete_user_by_id(test_user.id)
    
    test_user = API.db.index.create_user('test-user', 'test')

    response = client.post("/login", data = {
        'username' : 'test-user',
        'password' : 'test'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/admin/'

    invalid_response = client.post("/login", data = {
        'username' : 'invalid-test-user',
        'password' : 'invalid-password'
    }, follow_redirects=True)

    assert invalid_response.status_code == 200
    assert invalid_response.request.path == '/login'

    # Check that it redirects
    response = client.post("/login", data = {
        'username' : 'test-user',
        'password' : 'test'
    }, follow_redirects=False)
    assert response.status_code == 302

    # Check that it redirects the user back to /login if they don't fill in a username or password
    empty_form_response = client.post('/login', data = {
        'username' : 'test',
        'password' : ''
    }, follow_redirects=True)
    assert empty_form_response.status_code == 200
    assert empty_form_response.request.path == '/login'
    # Check that it redirects the user if they don't fill in username or password
    empty_form_response = client.post('/login', data = {
        'username' : 'test',
        'password' : ''
    }, follow_redirects=False)
    assert empty_form_response.status_code == 302
    assert empty_form_response.request.path == '/login'


    API.db.index.delete_user_by_id(test_user.id)
    
def test_logout(client):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    # Check there was only one redirect response
    assert len(response.history) == 1


    # Check that it does redirect
    redirect_response = client.get('/logout', follow_redirects=False)
    assert redirect_response.status_code == 302

def test_check_access_forbidden(client):
    """Check that the user can't access the model views when they aren't signed in"""
    user_response = client.get('/admin/user', follow_redirects=True)
    assert user_response.status_code == 403
    vehicle_response = client.get('/admin/vehicle', follow_redirects=True)
    assert vehicle_response.status_code == 403

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

    
# def test_fail():
#     assert 1 == 2
