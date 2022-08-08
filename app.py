import json
from time import strftime
from datetime import datetime, timedelta
import difflib
from threading import Thread
# Flask Imports
from flask import Flask, Response
from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
# Slack Imports
from slackeventsapi import SlackEventAdapter
from slack_sdk import WebClient
# Local Imports
import API.Calendar
from models import Vehicle, User
from models import db
from config import SLACK_SIGNING_SECRET, slack_token, user_token, VERIFICATION_TOKEN
import API.db.index
import routes


# This function is required or else there will be a context error
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app
app = create_app()
app.app_context().push()
with app.app_context():
    db.create_all()

# Define routes
app.add_url_rule('/login', view_func=routes.login, methods=['POST', 'GET'])
app.add_url_rule('/logout', view_func=routes.logout, methods = ['POST', 'GET'])
app.add_url_rule('/create/new/user', view_func=routes.create_new_user, methods = ['POST'])
app.add_url_rule('/interactions', view_func=routes.interactions, methods = ['POST'])
app.add_url_rule('/', view_func=routes.event_hook)
########

migrate = Migrate(app, db)
app.config.from_pyfile('config.py')

# toolbar = DebugToolbarExtension(app) # tool bar only works when app.debug is True
login = LoginManager(app)


# Creates Admin User if there is no users in the database
def create_admin_user():
    API.db.index.create_user('admin', 'password')

if (len(API.db.index.get_all_users()) == 0):
    create_admin_user()


@login.user_loader
def load_user(user_id):
    return API.db.index.get_user_by_id(user_id)

class MyModelView(ModelView):
    """Overide's flask_admin ModelView so that way it only displays if you are authenticated to see it"""
    def is_accessible(self):
        return current_user.is_authenticated

class MyUserView(ModelView):
    """Overide's flask_admin ModelView so that way it only displays if you are authenticated to see it"""
    def is_accessible(self):
        return current_user.is_authenticated
    @expose('/new', methods=('GET', 'POST'))
    def create_view(self):
        """
        Custom create view.
        """
        return self.render('user_create.html')

admin = Admin(app, name='Vehicle Reservation', template_mode='bootstrap3')
# Creates Admin Page
admin.add_view(MyUserView(User, db.session))
admin.add_view(MyModelView(Vehicle, db.session))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

#instantiating slack client
slack_client = WebClient(token=slack_token)
user_client = WebClient(user_token)


# COMMANDS
RESERVE_COMMAND = "reserve"
GET_ALL_RESERVATIONS_COMMAND = "reservations"
VEHICLES_COMMAND = "vehicles"
CHECK_VEHICLE_COMMAND = "check"
HELP_COMMAND = "help"

vehicle_names = API.db.index.get_vehicle_names()
    
slack_events_adapter = SlackEventAdapter(
    SLACK_SIGNING_SECRET, "/slack/events", app
)  

def check_available(vehicle, start_time, end_time):
    available = API.Calendar.check_if_reservation_available(vehicle.calendarGroupID, vehicle.calendarID, start_time, end_time)
    return available

def get_selected_vehicle_name_from_payload(payload):
    selected_option = list(payload['state']['values'].items())[0][1]['static_select-action']['selected_option']
    if selected_option is None:
        return selected_option
    else:
        vehicle_name = selected_option.get('text').get('text', None)
        return vehicle_name

def get_start_end_time_from_payload(payload):
    state = list(payload['state']['values'].items())
    start_date = state[1][1]['datepicker-action']['selected_date']
    start_time = state[2][1]['timepicker-action']['selected_time']
    end_date = state[3][1]['datepicker-action']['selected_date']
    end_time = state[4][1]['timepicker-action']['selected_time']
    start = f"{start_date}T{start_time}"
    end = f"{end_date}T{end_time}"
    return (start, end)

def reserve_vehicle(payload, selected_vehicle):
    """Uses the api to check that vehicle is available. If it is, it will reserve the vehicle

    Keyword arguments\n
            payload   --    The slack block payload that was sent from submitting the reserve block\n
            selected_vehicle -- The vehicle the user selected to reserve
    """
    vehicle = API.db.index.get_vehicle_by_name(selected_vehicle)
    start_time, end_time = get_start_end_time_from_payload(payload)
    users_name = list(payload['state']['values'].items())[5][1]['plain_text_input-action']['value']
    channel_id = payload['channel']['id']
    user_id = payload['user']['id']
    thread_id = payload['message']['ts']
    if start_time == 'NoneTNone' or end_time == 'NoneTNone':
        send_ephemeral_message("Time of reservation is required", channel_id, user_id, thread_id)
        return {'status': 400}
    if not users_name:
        send_ephemeral_message("Name is required for reservation", channel_id, user_id, thread_id)
        return {'status': 400}
    try:
        available = check_available(vehicle, start_time, end_time)
        if not available:
            send_ephemeral_message(f"{selected_vehicle} is not available at that time", channel_id, user_id, thread_id)
            return {'status': 400} # NOTE These return statements are not necessary. Used for testing
        else:
            response = API.Calendar.schedule_event(vehicle.calendarGroupID, vehicle.calendarID, start_time, end_time, users_name)
            if "ERROR" in response:
                send_ephemeral_message(f"{response['ERROR']}", channel_id, user_id, thread_id)
                return {'status': 500}
            else:
                send_ephemeral_message(f"{selected_vehicle} was successfully reserved", channel_id, user_id, thread_id)
                return {'status': 200}
    except:
        send_ephemeral_message(f"Sorry, an error has occured, so I was unable to complete your request", channel_id, user_id, thread_id)
        return {'status': 500}

def check_vehicle(payload, selected_vehicle):
        """Checks a specific vehicle from start time to end time

        Keyword arguments\n
                payload   --    The slack block payload that was sent from submitting the check_vehicle slack block\n
                selected_vehicle -- The vehicle the user selected
        """
        vehicle = API.db.index.get_vehicle_by_name(selected_vehicle)
        start_time, end_time = get_start_end_time_from_payload(payload)
        channel_id = payload['channel']['id']
        user_id = payload['user']['id']
        thread_id = payload['message']['ts']
        try:
            available = check_available(vehicle, start_time, end_time)
            if not available:
                send_ephemeral_message(f"{selected_vehicle} is not available at that time", channel_id, user_id, thread_id)
                return {'status': 400}
            else:
                send_ephemeral_message(f"{selected_vehicle} is available at that time", channel_id, user_id, thread_id)
                return {'status': 200}
        except:
            send_ephemeral_message(f"Sorry, an error has occured, so I was unable to complete your request", channel_id, user_id, thread_id)
            return {'status': 500}

def get_reservations(payload, selected_vehicle):
    """Gets all of the reservations for the selected_vehicle

    Keyword arguments\n
        payload   --    The slack block payload that was sent\n
        selected_vehicle -- The vehicle the user selected
    """
    vehicle = API.db.index.get_vehicle_by_name(selected_vehicle)
    channel_id = payload['channel']['id']
    user_id = payload['user']['id']
    thread_id = payload['message']['ts']
    try:
        events = API.Calendar.list_specific_calendar_in_group_events(vehicle.calendarGroupID, vehicle.calendarID)
        res = API.Calendar.construct_calendar_events_block(events, selected_vehicle)
        if res['reservations'] == False:
            send_ephemeral_message(
                f'There are no reservations for {selected_vehicle}',
                channel_id,
                user_id,
                thread_id
            )
            return {'status': 200, 'reservations': False}
        else:
            with open('slack_blocks/reservations_results.json', 'r') as f:
                data = json.load(f)
            send_ephemeral_message(
                "Here are the reservations",
                channel_id,
                user_id,
                thread_id,
                data['blocks']
            )
            return {'status': 200, 'reservations': True}
    except:
        send_ephemeral_message(
            f"Sorry, an error has occured, so I was unable to complete your request",
            channel_id,
            user_id,
            thread_id
        )
        return {'status': 500}
        
def create_vehicle_options_slack_block():
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

def get_slack_block_and_add_vehicles(path_to_file):
    """Gets the slack block that is at path_to_file then it adds all of the vehicle options to that block

    Keyword arguments\n
        path_to_file  -- The path to the slack block
    """
    vehicle_options = create_vehicle_options_slack_block()
    with open(path_to_file) as f:
        data = json.load(f)
    data['blocks'][1]['element']['options'] = vehicle_options
    with open(path_to_file, "w") as write_f:
        json.dump(data, write_f)    
    with open(path_to_file, "r") as new_f:
        new_data = json.load(new_f)
    return new_data

def construct_vehicles_command():
    offset_minutes = 15 # 15 Minute offset for check availability
    start_time = strftime("%Y-%m-%dT%H:%M")

    offset_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M') + timedelta(minutes=offset_minutes)
    end_time = offset_time.strftime('%Y-%m-%dT%H:%M')

    with open("slack_blocks/vehicles_results.json", "r+") as f:
        f.truncate(0) # Clear the json file

    vehicles_block = {
        "blocks": []
    }
    with app.app_context():
        for vehicle in API.db.index.get_all_vehicles():
            available = check_available(vehicle, start_time, end_time)
            availablity_message = "available" if available else "not available"
            vehicles_block['blocks'].append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{vehicle.name} - *{availablity_message}*"
                    }
                }
            )
    with open('slack_blocks/vehicles_results.json', 'w') as f:
        json.dump(vehicles_block, f)


@slack_events_adapter.on("app_mention")
def handle_message(event_data):
    def send_reply(value):
        """ Reads the command given in slack and responds depending on what the user's input was
    
            Keyword arguments\n
            value   -- A dictionary that contains important information like team_id, event information, ect. The main important one is the event sub-dictionary because it contains the message and user
        """
        event_data = value
        message = event_data["event"]
        if message.get("subtype") is None:
            commands = message.get('text').split()
            channel_id = message["channel"]
            if len(commands) == 1:
                send_ephemeral_message("Did not provide a command", channel_id, get_user_slack_id(), message['ts'])
                return
            command = commands[1]
            # This is where slack messages are handled
            """Makes an event on the calendar."""            
            if command.lower() == RESERVE_COMMAND:
                data = get_slack_block_and_add_vehicles('slack_blocks/reserve_block.json')
                slack_client.chat_postMessage(channel = channel_id, thread_ts=message['ts'], text = "Please fill out the form", blocks = data['blocks'])
                return
                                
            """Gets reservations on the calendar"""
            if command.lower() == GET_ALL_RESERVATIONS_COMMAND:
                data = get_slack_block_and_add_vehicles('slack_blocks/reservations_block.json')
                slack_client.chat_postMessage(channel = channel_id, thread_ts=message['ts'], text = "Please fill out the form", blocks = data['blocks'])
                return

            """Check if vehicle is available from start_time to end_time"""
            if command.lower() == CHECK_VEHICLE_COMMAND:    
                data = get_slack_block_and_add_vehicles('slack_blocks/check_vehicle_block.json')
                slack_client.chat_postMessage(channel = channel_id, thread_ts=message['ts'], text = "Please fill out the form", blocks = data['blocks'])
                return

            """Lists all of the vehicle's names and displays if they are available"""
            if command.lower() == VEHICLES_COMMAND:
                construct_vehicles_command()
                with open('slack_blocks/vehicles_results.json', 'r') as f:
                    data = json.load(f)
                send_ephemeral_message("List of vehicles", channel_id, get_user_slack_id(), message['ts'], data['blocks'])
                return
            
            if command.lower() == HELP_COMMAND:
                with open('slack_blocks/help_block.json') as f:
                    data = json.load(f)
                slack_client.chat_postMessage(text="Here is the usage manual", channel=channel_id, thread_ts=message['ts'], blocks = data['blocks'] )
                return
            else: #Command that was used doesn't exist. Tries to get closest command to what the user typed
                similar_commands = difflib.get_close_matches(command.lower(), [RESERVE_COMMAND, GET_ALL_RESERVATIONS_COMMAND, VEHICLES_COMMAND, HELP_COMMAND, CHECK_VEHICLE_COMMAND])
                similar_command_response = ''
                index = 0
                for item in similar_commands:
                    index += 1
                    if index >= len(similar_commands):
                        similar_command_response += item
                    else:
                        similar_command_response += (item + ', ')
                if similar_command_response:
                    response_text = f"Did not recognize command: {command.lower()}\nDid you mean to use the command: {similar_command_response}?"
                else:
                    response_text = f"Did not recognize command: {command.lower()}"
                slack_client.chat_postMessage(text=response_text, channel=channel_id, thread_ts=message['ts'] )
                return
        
    thread = Thread(target=send_reply, kwargs={"value": event_data})
    thread.start()
    return Response(status=200)

def get_user_slack_id():
    return user_client.users_identity()['user']['id'] 

def send_direct_message(response_text):
    user_slack_id = get_user_slack_id()
    slack_client.chat_postEphemeral(channel=user_slack_id, text=response_text, user=user_slack_id)

def send_ephemeral_message(text, channel_id, user_id, ts_id, blocks=''):
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


if __name__ == "__main__":
    app.run(port=3000)