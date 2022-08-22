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
    

    def send_ephemeral_message(text, channel_id, user_id, ts_id, slack_client, blocks=''):
        print(f"Text: {text}\n Channel Id: {channel_id}\n User Id: {user_id}\n Thread Id: {ts_id}\n Slack Client : {slack_client}\n Block: {blocks}\n")
        if blocks == '':
            slack_client.chat_postEphemeral(
                channel=channel_id,
                text=text,
                user=user_id,
                thread_ts=ts_id,
            )
        else:
            slack_client.chat_postEphemeral(
                channel=channel_id,
                text=text,
                user=user_id,
                thread_ts=ts_id,
                blocks=blocks
            )