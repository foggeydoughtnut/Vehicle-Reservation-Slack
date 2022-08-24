from app.slack_bot import Slack_Bot_Logic
import json

slack_bot = Slack_Bot_Logic()

with open('tests/valid_payload.json') as f:
    test_payload = json.load(f)

def test_get_selected_vehicle_name_from_payload():
    vehicle_name = slack_bot.get_selected_vehicle_name_from_payload(test_payload)
    assert vehicle_name == 'test1'

def test_start_end_time_from_payload():
    start, end = slack_bot.get_start_end_time_from_payload(test_payload)
    assert start == '2022-07-07T13:00'
    assert end == '2022-07-07T14:00'

class Vehicle:
    name = 'test_name'
    calendarGroupID = 'test_calendar_group_id'
    calendarID = 'test_calendar_id'

def test_check_available(mocker):
    mocker.patch('api.Calendar.check_if_reservation_available', return_value=True)
    vehicle = Vehicle()
    available = slack_bot.check_available(vehicle, 'start_time', 'end_time')
    assert available == True

def test_reserve_vehicle_successfull(mocker):
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch.object(Slack_Bot_Logic, 'check_available', return_value=True)
    mocker.patch('api.Calendar.schedule_event', return_value={"SUCCESS" : "Successfully created an event"})
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='SUCCESS')
    res = slack_bot.reserve_vehicle(test_payload, 'test')
    assert res['status'] == 200

def test_reserve_vehicle_error_schedule(mocker):
    """Returns a 500 error when api.Calendar.schedule_event returns an error"""
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch.object(Slack_Bot_Logic, 'check_available', return_value=True)
    mocker.patch('api.Calendar.schedule_event', return_value={"ERROR" : "An error occured"})
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    res = slack_bot.reserve_vehicle(test_payload, 'test')
    assert res['status'] == 500

def test_reserve_vehicle_not_available(mocker):
    """Returns a 400 status if the vehicle is not available"""
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch.object(Slack_Bot_Logic, 'check_available', return_value=False)
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    res = slack_bot.reserve_vehicle(test_payload, 'test')
    assert res['status'] == 400

def test_reserve_vehicle_exception(mocker):
    """Returns status of 500 when exception occurs"""
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch.object(Slack_Bot_Logic, 'check_available', side_effect=Exception("mocked error"))
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    res = slack_bot.reserve_vehicle(test_payload, 'test')
    assert res['status'] == 500

def test_reserve_vehicle_no_name(mocker):
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    with open('tests/no_name_payload.json') as f:
        payload = json.load(f)
    res = slack_bot.reserve_vehicle(payload, 'test')
    assert res['status'] == 400

def test_reserve_vehicle_no_date_time(mocker):
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    mocker.patch.object(Slack_Bot_Logic, 'get_start_end_time_from_payload', return_value=('NoneTNone', 'NoneTNone'))
    res = slack_bot.reserve_vehicle(test_payload, 'test')
    assert res['status'] == 400

def test_reserve_vehicle_missing_time(mocker):
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    mocker.patch.object(Slack_Bot_Logic, 'get_start_end_time_from_payload', return_value=('2022-08-10TNone', '2022-08-10TNone'))
    res = slack_bot.reserve_vehicle(test_payload, 'test')
    assert res['status'] == 400

def test_reserve_vehicle_missing_date(mocker):
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    mocker.patch.object(Slack_Bot_Logic, 'get_start_end_time_from_payload', return_value=('NoneT13:00', 'NoneT14:00'))
    res = slack_bot.reserve_vehicle(test_payload, 'test')
    assert res['status'] == 400

def test_check_vehicle_success(mocker):
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch.object(Slack_Bot_Logic, 'check_available', return_value=True)
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    res = slack_bot.check_vehicle(test_payload, 'test')
    assert res['status'] == 200

def test_check_vehicle_unavailable(mocker):
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch.object(Slack_Bot_Logic, 'check_available', return_value=False)
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    res = slack_bot.check_vehicle(test_payload, 'test')
    assert res['status'] == 400

def test_check_vehicle_exception(mocker):
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch.object(Slack_Bot_Logic, 'check_available', side_effect=Exception('mocked exception'))
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    res = slack_bot.check_vehicle(test_payload, 'test')
    assert res['status'] == 500

def test_check_vehicle_no_date_time(mocker):
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    mocker.patch.object(Slack_Bot_Logic, 'get_start_end_time_from_payload', return_value=('NoneTNone', 'NoneTNone'))
    res = slack_bot.check_vehicle(test_payload, 'test')
    assert res['status'] == 400

def test_check_vehicle_missing_time(mocker):
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    mocker.patch.object(Slack_Bot_Logic, 'get_start_end_time_from_payload', return_value=('2022-08-10TNone', '2022-08-10TNone'))
    res = slack_bot.check_vehicle(test_payload, 'test')
    assert res['status'] == 400

def test_check_vehicle_missing_date(mocker):
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    mocker.patch.object(Slack_Bot_Logic, 'get_start_end_time_from_payload', return_value=('NoneT13:00', 'NoneT14:00'))
    res = slack_bot.check_vehicle(test_payload, 'test')
    assert res['status'] == 400

def test_get_reservations(mocker):
    """Returns a status of 200 when no exceptions and returns that there are reservations"""
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch('api.Calendar.list_specific_calendar_in_group_events', return_value={})
    mocker.patch('api.Calendar.construct_calendar_events_block', return_value = {'reservations' : True})
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    res = slack_bot.get_reservations(test_payload, 'test')
    assert res['status'] == 200
    assert res['reservations'] == True

def test_get_reservations_no_reservations(mocker):
    """Returns a status of 200 when no exceptions and returns false when there are no reservations"""
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch('api.Calendar.list_specific_calendar_in_group_events', return_value={})
    mocker.patch('api.Calendar.construct_calendar_events_block', return_value = {'reservations' : False})
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    res = slack_bot.get_reservations(test_payload, 'test')
    assert res['status'] == 200
    assert res['reservations'] == False

def test_get_reservations_excpetion(mocker):
    """Tests that 500 status is returned when exception occurs"""
    mocker.patch('api.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch('api.Calendar.list_specific_calendar_in_group_events', side_effect=Exception('mocked exception'))
    mocker.patch.object(Slack_Bot_Logic, 'send_ephemeral_message', return_value='')
    res = slack_bot.get_reservations(test_payload, 'test')
    assert res['status'] == 500

def test_construct_vehicles_command(mocker):
    expected = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "test_name - *available*"
                }
            }
        ]
    }
    mocker.patch('api.db.index.get_all_vehicles', return_value=[Vehicle()])
    mocker.patch.object(Slack_Bot_Logic, 'check_available', return_value=True)
    slack_bot.construct_vehicles_command([])

    with open('app/slack_blocks/vehicles_results.json', 'r') as f:
        data = json.load(f)
    # See https://stackoverflow.com/questions/46914222/how-can-i-assert-lists-equality-with-pytest
    assert len(data) == len(expected)
    assert all([a == b for a, b in zip(data, expected)])

def test_find_similar_commands_one_similar():
    response = slack_bot.find_similar_commands('hel')
    split_response = response.split('\n')
    assert 'hel' in split_response[0]
    assert 'help' in split_response[1]

def test_find_similar_commands_two_similar():
    response = slack_bot.find_similar_commands('reserv')
    split_response = response.split('\n')
    assert 'reserv' in split_response[0]
    assert 'commands' in split_response[1] # Tests that it pluralized command when there is more than one similar command
    assert 'reserve' in split_response[1]
    assert 'reservations' in split_response[1]

def test_find_similar_commands_no_similar():
    response = slack_bot.find_similar_commands('asdf')
    assert 'asdf' in response
    assert 'Did you mean to use the commands:' not in response
