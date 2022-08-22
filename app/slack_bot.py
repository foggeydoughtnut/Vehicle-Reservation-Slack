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