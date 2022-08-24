import difflib
import json
from time import time, strftime
from datetime import datetime, timedelta

# Slack Imports
from slack_sdk import WebClient

# Local Imports
from config import VERIFICATION_TOKEN, slack_token
import api.Calendar
import api.db.index



class Slack_Bot_Commands:
    RESERVE_COMMAND = "reserve"
    GET_ALL_RESERVATIONS_COMMAND = "reservations"
    VEHICLES_COMMAND = "vehicles"
    CHECK_VEHICLE_COMMAND = "check"
    HELP_COMMAND = "help"

class Slack_Bot_Logic:

    

    def __init__(self):
        self.slack_client = WebClient(token=slack_token)
        self.commands = Slack_Bot_Commands()

    def send_ephemeral_message(self, text, channel_id, user_id, ts_id, blocks=''):
        if blocks == '':
            self.slack_client.chat_postEphemeral(
                channel=channel_id,
                text=text,
                user=user_id,
                thread_ts=ts_id,
            )
        else:
            self.slack_client.chat_postEphemeral(
                channel=channel_id,
                text=text,
                user=user_id,
                thread_ts=ts_id,
                blocks=blocks
            )

    
    def find_similar_commands(self, command):
        """Command that was used doesn't exist. Tries to get the closest command to what the user typed

        Keyword arguments\n
            command - The command the user typed in
        """
        similar_commands = difflib.get_close_matches(
            command.lower(),
            [
                self.commands.RESERVE_COMMAND,
                self.commands.GET_ALL_RESERVATIONS_COMMAND,
                self.commands.VEHICLES_COMMAND,
                self.commands.HELP_COMMAND,
                self.commands.CHECK_VEHICLE_COMMAND
            ]
        )
        similar_command_response = ''
        index = 0
        for item in similar_commands:
            index += 1
            if index >= len(similar_commands):
                similar_command_response += item
            else:
                similar_command_response += (item + ', ')
        if similar_command_response:
            return f"Did not recognize command: {command.lower()}\nDid you mean to use the command{'s' if len(similar_commands) > 1 else ''}: " \
                            f"{similar_command_response}? "
        else:
            return f"Did not recognize command: {command.lower()}"

    def get_selected_vehicle_name_from_payload(payload):
        selected_option = list(payload['state']['values'].items())[0][1]['static_select-action']['selected_option']
        if selected_option is None:
            return selected_option
        else:
            vehicle_name = selected_option.get('text').get('text', None)
            return vehicle_name

    def get_start_end_time_from_payload(self, payload):
        """Accesses the payload and gets the date and time information from the slack command

            Returns a tuple with start and end time that is formatted correctly for Graph api
        """
        state = list(payload['state']['values'].items())
        start_date = state[1][1]['datepicker-action']['selected_date']
        start_time = state[2][1]['timepicker-action']['selected_time']
        end_date = state[3][1]['datepicker-action']['selected_date']
        end_time = state[4][1]['timepicker-action']['selected_time']
        start = f"{start_date}T{start_time}"
        end = f"{end_date}T{end_time}"
        return start, end


    def validate_slack_message(self, request):
        """Validates slack message using the verfication token.\n
            TODO: Verifcation tokens are going to be depracated. Use the slack-signing-secret method instead.\n
            https://api.slack.com/authentication/verifying-requests-from-slack
        """
        timestamp = request['event_time']
        if abs(time() - timestamp) > 60 * 5:
            return False
        token = request["token"]
        if token != VERIFICATION_TOKEN:
            return False
        return True


    def create_vehicle_options_slack_block(self, vehicle_names):
        """Creates the vehicle_options that will be used in the get_slack_block_and_add_vehicles method"""
        vehicle_options = []
        i = 0
        for vehicle in vehicle_names:
            vehicle_obj = {
                "text": {
                    "type": "plain_text",
                    "text": f"{vehicle}"
                },
                "value": f"value-{i}"
            }
            vehicle_options.append(vehicle_obj)
            i += 1
        return vehicle_options


    def get_slack_block_and_add_vehicles(self, path_to_file, vehicle_names):
        """Gets the slack block that is at path_to_file then it adds all the vehicle options to that block

        Keyword arguments\n
            path_to_file  -- The path to the slack block
        """
        vehicle_options = self.create_vehicle_options_slack_block(vehicle_names)
        with open(path_to_file) as f:
            data = json.load(f)
        data['blocks'][1]['element']['options'] = vehicle_options
        with open(path_to_file, "w") as write_f:
            json.dump(data, write_f)
        with open(path_to_file, "r") as new_f:
            new_data = json.load(new_f)
        return new_data


    def check_available(self, vehicle, start_time, end_time):
        available = api.Calendar.check_if_reservation_available(
            vehicle.calendarGroupID,
            vehicle.calendarID,
            start_time,
            end_time
        )
        return available


    def get_reservations(self, payload, selected_vehicle):
        """Gets all the reservations for the selected_vehicle
        Keyword arguments\n
            payload   --    The slack block payload that was sent\n
            selected_vehicle -- The vehicle the user selected
        """
        vehicle = api.db.index.get_vehicle_by_name(selected_vehicle)
        channel_id = payload['channel']['id']
        user_id = payload['user']['id']
        thread_id = payload['message']['ts']
        try:
            events = api.Calendar.list_specific_calendar_in_group_events(vehicle.calendarGroupID, vehicle.calendarID)
            res = api.Calendar.construct_calendar_events_block(events, selected_vehicle)
            if not res['reservations']:
                self.send_ephemeral_message(
                    f'There are no reservations for {selected_vehicle}',
                    channel_id,
                    user_id,
                    thread_id,
                )
                return {'status': 200, 'reservations': False}
            else:
                with open('app/slack_blocks/reservations_results.json', 'r') as f:
                    data = json.load(f)
                self.send_ephemeral_message(
                    "Here are the reservations",
                    channel_id,
                    user_id,
                    thread_id,
                    data['blocks']
                )
                return {'status': 200, 'reservations': True}
        except:
            self.send_ephemeral_message(
                f"Sorry, an error has occurred, so I was unable to complete your request",
                channel_id,
                user_id,
                thread_id,
            )
            return {'status': 500}


    def construct_vehicles_command(self, vehicles):
        """Constructs the vehicle slack block.
        This is what adds the vehicles to the block and adds if they are available or not"""
        offset_minutes = 15  # 15 Minute offset for check availability
        start_time = strftime("%Y-%m-%dT%H:%M")

        offset_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M') + timedelta(minutes=offset_minutes)
        end_time = offset_time.strftime('%Y-%m-%dT%H:%M')

        with open("app/slack_blocks/vehicles_results.json", "r+") as f:
            f.truncate(0)  # Clear the json file

        vehicles_block = {
            "blocks": []
        }
        for vehicle in vehicles:
            available = self.check_available(vehicle, start_time, end_time)
            availability_message = "available" if available else "not available"
            vehicles_block['blocks'].append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{vehicle.name} - *{availability_message}*"
                    }
                }
            )
        with open('app/slack_blocks/vehicles_results.json', 'w') as f:
            json.dump(vehicles_block, f)

        