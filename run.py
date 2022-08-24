import json
from time import strftime, time
from datetime import datetime, timedelta
from threading import Thread
# Flask Imports
from flask import Flask, Response, render_template
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user
# Slack Imports
from slackeventsapi import SlackEventAdapter
from slack_sdk import WebClient
# Local Imports
import api.Calendar
from app.models import Vehicle, User
from app.models import db
from config import SLACK_SIGNING_SECRET, VERIFICATION_TOKEN, slack_token, user_token
import api.db.index
from app.views import login, logout, create_new_user, interactions, event_hook
from app.links import links
from app.slack_bot import Slack_Bot_Commands, Slack_Bot_Logic

# This function is required or else there will be a context error
def create_app():
    new_app = Flask(__name__, template_folder='./app/templates', static_folder='./app/static')
    new_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    new_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(new_app)

    # Define views
    new_app.add_url_rule(links.login, view_func=login, methods=['POST', 'GET'])
    new_app.add_url_rule(links.logout, view_func=logout, methods=['POST', 'GET'])
    new_app.add_url_rule(links.create_new_user, view_func=create_new_user, methods=['POST'])
    new_app.add_url_rule(links.interactions, view_func=interactions, methods=['POST'])
    new_app.add_url_rule(links.home, view_func=event_hook)
    ########
    return new_app


app = create_app()
app.app_context().push()
with app.app_context():
    db.create_all()


def page_not_found(e):
    return render_template('404.html'), 404
app.register_error_handler(404, page_not_found)

app.config.from_pyfile('config.py')
login = LoginManager(app)


# Creates Admin User if there is no users in the database
def create_admin_user():
    api.db.index.create_user('admin', 'password')


if len(api.db.index.get_all_users()) == 0:
    create_admin_user()


@login.user_loader
def load_user(user_id):
    return api.db.index.get_user_by_id(user_id)


class MyModelView(ModelView):
    """Override's flask_admin ModelView so that way it only displays if you are authenticated to see it"""

    def is_accessible(self):
        return current_user.is_authenticated


class MyUserView(ModelView):
    """Override's flask_admin ModelView so that way it only displays if you are authenticated to see it"""

    def is_accessible(self):
        return current_user.is_authenticated

    @expose('/new', methods=('GET', 'POST'))
    def create_view(self):
        """
        Custom create view.
        """
        return self.render('user_create.html')


class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        text = 'Log In' if not current_user.is_authenticated else 'Log Out'
        return self.render('admin/index.html', button_text=text)


admin = Admin(
    app,
    template_mode='bootstrap3',
    index_view=MyHomeView()
)
# Creates Admin Page
admin.add_view(MyUserView(User, db.session))
admin.add_view(MyModelView(Vehicle, db.session))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

""" Slack Bot Setup and command logic """
# instantiating slack client
slack_client = WebClient(token=slack_token)
user_client = WebClient(user_token)

# COMMANDS
# RESERVE_COMMAND = "reserve"
# GET_ALL_RESERVATIONS_COMMAND = "reservations"
# VEHICLES_COMMAND = "vehicles"
# CHECK_VEHICLE_COMMAND = "check"
# HELP_COMMAND = "help"

vehicle_names = api.db.index.get_vehicle_names()

slack_events_adapter = SlackEventAdapter(
    SLACK_SIGNING_SECRET, "/slack/events", app
)
slack_bot = Slack_Bot_Logic()


def check_available(vehicle, start_time, end_time):
    available = api.Calendar.check_if_reservation_available(vehicle.calendarGroupID, vehicle.calendarID, start_time,
                                                            end_time)
    return available


def reserve_vehicle(payload, selected_vehicle):
    """Uses the api to check that vehicle is available. If it is, it will reserve the vehicle

    Keyword arguments\n
            payload   --    The slack block payload that was sent from submitting the reserve block\n
            selected_vehicle -- The vehicle the user selected to reserve
    """
    vehicle = api.db.index.get_vehicle_by_name(selected_vehicle)
    start_time, end_time = slack_bot.get_start_end_time_from_payload(payload)
    users_name = list(payload['state']['values'].items())[5][1]['plain_text_input-action']['value']
    channel_id = payload['channel']['id']
    user_id = payload['user']['id']
    thread_id = payload['message']['ts']
    if 'None' in start_time or 'None' in end_time:
        slack_bot.send_ephemeral_message("Time of reservation is required", channel_id, user_id, thread_id)
        return {'status': 400}
    if not users_name:
        slack_bot.send_ephemeral_message("Name is required for reservation", channel_id, user_id, thread_id)
        return {'status': 400}
    try:
        available = check_available(vehicle, start_time, end_time)
        if not available:
            slack_bot.send_ephemeral_message(f"{selected_vehicle} is not available at that time", channel_id, user_id, thread_id)
            return {'status': 400}  # NOTE These return statements are not necessary. Used for testing
        else:
            response = api.Calendar.schedule_event(vehicle.calendarGroupID, vehicle.calendarID, start_time, end_time,
                                                   users_name)
            if "ERROR" in response:
                slack_bot.send_ephemeral_message(f"{response['ERROR']}", channel_id, user_id, thread_id)
                return {'status': 500}
            else:
                slack_bot.send_ephemeral_message(f"{selected_vehicle} was successfully reserved", channel_id, user_id, thread_id)
                return {'status': 200}
    except:
        slack_bot.send_ephemeral_message(f"Sorry, an error has occurred, so I was unable to complete your request", channel_id,
                               user_id, thread_id)
        return {'status': 500}


def check_vehicle(payload, selected_vehicle):
    """Checks a specific vehicle from start time to end time
        Keyword arguments\n
            payload -- The slack block payload that was sent from submitting the check_vehicle slack block\n
            selected_vehicle -- The vehicle the user selected
        """
    vehicle = api.db.index.get_vehicle_by_name(selected_vehicle)
    start_time, end_time = slack_bot.get_start_end_time_from_payload(payload)
    channel_id = payload['channel']['id']
    user_id = payload['user']['id']
    thread_id = payload['message']['ts']
    if 'None' in start_time or 'None' in end_time:
        slack_bot.send_ephemeral_message("Time of reservation is required", channel_id, user_id, thread_id)
        return {'status': 400}
    try:
        available = check_available(vehicle, start_time, end_time)
        if not available:
            slack_bot.send_ephemeral_message(f"{selected_vehicle} is not available at that time", channel_id, user_id, thread_id)
            return {'status': 400}
        else:
            slack_bot.send_ephemeral_message(f"{selected_vehicle} is available at that time", channel_id, user_id, thread_id)
            return {'status': 200}
    except:
        slack_bot.send_ephemeral_message(f"Sorry, an error has occurred, so I was unable to complete your request", channel_id,
                               user_id, thread_id)
        return {'status': 500}


def get_reservations(payload, selected_vehicle):
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
            slack_bot.send_ephemeral_message(
                f'There are no reservations for {selected_vehicle}',
                channel_id,
                user_id,
                thread_id,
            )
            return {'status': 200, 'reservations': False}
        else:
            with open('app/slack_blocks/reservations_results.json', 'r') as f:
                data = json.load(f)
            slack_bot.send_ephemeral_message(
                "Here are the reservations",
                channel_id,
                user_id,
                thread_id,
                data['blocks']
            )
            return {'status': 200, 'reservations': True}
    except:
        slack_bot.send_ephemeral_message(
            f"Sorry, an error has occurred, so I was unable to complete your request",
            channel_id,
            user_id,
            thread_id,
        )
        return {'status': 500}


def construct_vehicles_command():
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
    with app.app_context():
        for vehicle in api.db.index.get_all_vehicles():
            available = check_available(vehicle, start_time, end_time)
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


@slack_events_adapter.on("app_mention")
def handle_message(event_data):
    def send_reply(value):
        """ Reads the command given in slack and responds depending on what the user's input was

            Keyword arguments\n
            value   -- A dictionary that contains important information like team_id, event information, ect. The main
            important one is the event sub-dictionary because it contains the message and user
        """
        valid = slack_bot.validate_slack_message(value)
        if not valid:
            return
        message = value["event"]
        if message.get("subtype") is None:
            commands = message.get('text').split()
            channel_id = message["channel"]
            if len(commands) == 1:
                slack_bot.send_ephemeral_message("Did not provide a command", channel_id, get_user_slack_id(), message['ts'])
                return
            command = commands[1]
            # This is where Slack messages are handled
            """Makes an event on the calendar."""
            if command.lower() == Slack_Bot_Commands.RESERVE_COMMAND:
                data = slack_bot.get_slack_block_and_add_vehicles('app/slack_blocks/reserve_block.json', vehicle_names)
                slack_client.chat_postMessage(channel=channel_id, thread_ts=message['ts'],
                                              text="Please fill out the form", blocks=data['blocks'])
                return

            """Gets reservations on the calendar"""
            if command.lower() == Slack_Bot_Commands.GET_ALL_RESERVATIONS_COMMAND:
                data = slack_bot.get_slack_block_and_add_vehicles('app/slack_blocks/reservations_block.json', vehicle_names)
                slack_client.chat_postMessage(channel=channel_id, thread_ts=message['ts'],
                                              text="Please fill out the form", blocks=data['blocks'])
                return

            """Check if vehicle is available from start_time to end_time"""
            if command.lower() == Slack_Bot_Commands.CHECK_VEHICLE_COMMAND:
                data = slack_bot.get_slack_block_and_add_vehicles('app/slack_blocks/check_vehicle_block.json', vehicle_names)
                slack_client.chat_postMessage(channel=channel_id, thread_ts=message['ts'],
                                              text="Please fill out the form", blocks=data['blocks'])
                return

            """Lists all of the vehicle's names and displays if they are available"""
            if command.lower() == Slack_Bot_Commands.VEHICLES_COMMAND:
                construct_vehicles_command()
                with open('app/slack_blocks/vehicles_results.json', 'r') as f:
                    data = json.load(f)
                slack_bot.send_ephemeral_message(
                    "List of vehicles",
                    channel_id,
                    get_user_slack_id(),
                    message['ts'],
                    data['blocks']
                )
                return

            """Displays the usage manual which contains what commands there are and how to use them"""
            if command.lower() == Slack_Bot_Commands.HELP_COMMAND:
                with open('app/slack_blocks/help_block.json') as f:
                    data = json.load(f)
                slack_client.chat_postMessage(text="Here is the usage manual", channel=channel_id,
                                              thread_ts=message['ts'], blocks=data['blocks'])
                return
            else:
                """No command matched the available commands. Tries to find similar command for what the user typed"""
                response_text = slack_bot.find_similar_commands(command)
                slack_client.chat_postMessage(text=response_text, channel=channel_id, thread_ts=message['ts'])
                return

    thread = Thread(target=send_reply, kwargs={"value": event_data})
    thread.start()
    return Response(status=200)


def get_user_slack_id():
    return user_client.users_identity()['user']['id']


def send_direct_message(response_text):
    user_slack_id = get_user_slack_id()
    slack_client.chat_postEphemeral(channel=user_slack_id, text=response_text, user=user_slack_id)


if __name__ == "__main__":
    app.run(port=3000)
