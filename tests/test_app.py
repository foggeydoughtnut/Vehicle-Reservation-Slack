import pytest
from app import create_data_dict

def test_create_data_dict():
    valid_input_data = ['slack_user_id', 'command', 'vehicle_name', 'from', 'date_start', 'time_start', 'to', 'date_end', 'time_end']
    data = create_data_dict(valid_input_data)
    assert type(data) == dict
    assert data['command'] == 'vehicle_name'
    assert data['from'] == 'date_startTtime_start'
    assert data['to'] == 'date_endTtime_end'

    invalid_input_data = ['slack_user_id', 'command']
    error_data = create_data_dict(invalid_input_data)
    assert type(data) == dict
    assert error_data["Error"]


