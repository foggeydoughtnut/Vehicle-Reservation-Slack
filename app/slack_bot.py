import difflib

# Slack Imports
from slack_sdk import WebClient

# Local Imports
from config import slack_token


class Slack_Bot_Commands:
    RESERVE_COMMAND = "reserve"
    GET_ALL_RESERVATIONS_COMMAND = "reservations"
    VEHICLES_COMMAND = "vehicles"
    CHECK_VEHICLE_COMMAND = "check"
    HELP_COMMAND = "help"

class Slack_Bot_Logic():

    

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

    