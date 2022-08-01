from app import get_selected_vehicle_name_from_payload, get_start_end_time_from_payload, check_available, reserve_vehicle, check_vehicle, get_reservations
import json


with open('tests/valid_payload.json') as f:
    test_payload = json.load(f)

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

def test_reserve_vehicle_no_name(mocker):
    mocker.patch('API.db.index.get_vehicle_by_name', return_value=Vehicle())
    mocker.patch('app.send_message', return_value='')
    with open('tests/no_name_payload.json') as f:
        payload = json.load(f)
    res = reserve_vehicle(payload, 'test')
    assert res['status'] == 400

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