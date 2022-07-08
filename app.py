from concurrent.futures import thread
from distutils.command.build_scripts import first_line_re
import json
from time import strftime
from datetime import datetime, timedelta
from urllib import request
import requests
from urllib.parse import parse_qs
# Flask Imports
from flask import Flask, Response, redirect, request, render_template, session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
# Slack Imports
from slackeventsapi import SlackEventAdapter
from slack import WebClient
from threading import Thread
# Local Imports
import API.Calendar
import API.admin.user
from models import Vehicle, User
from models import db
from config import SLACK_SIGNING_SECRET, slack_token, user_token, VERIFICATION_TOKEN
import API.db.index



# This function is required or else there will be a context error
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    db.init_app(app)
    return app
app = create_app()
app.app_context().push()
with app.app_context():
    db.create_all()

# Creates Admin User if there is no users in the database
def create_admin_user():
    admin = API.db.index.create_user('admin', 'password')

if (len(API.db.index.get_all_users()) == 0):
    create_admin_user()
    


migrate = Migrate(app, db)
app.config.from_pyfile('config.py')
toolbar = DebugToolbarExtension(app) # tool bar only works when app.debug is True
login = LoginManager(app)


@login.user_loader
def load_user(user_id):
    return API.db.index.get_user_by_id(user_id)

class MyModelView(ModelView):
    """Overide's flask_admin ModelView so that way it only displays if you are authenticated to see it"""
    def is_accessible(self):
        return current_user.is_authenticated
    
# Creates Admin Page
admin = Admin(app, name='Vehicle Reservation', template_mode='bootstrap3')
admin.add_view(MyModelView(Vehicle, db.session))
admin.add_view(MyModelView(User, db.session))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

#instantiating slack client
slack_client = WebClient(slack_token)    
user_client = WebClient(user_token)


# COMMANDS
RESERVE_COMMAND = "reserve"
GET_ALL_RESERVATIONS_COMMAND = "reservations"
VEHICLES_COMMAND = "vehicles"
CHECK_VEHICLE_COMMAND = "check"
HELP_COMMAND = "help"

vehicle_names = API.db.index.get_vehicle_names()

@app.route("/")
def event_hook(request):
    json_dict = json.loads(request.body.decode("utf-8"))
    if json_dict["token"] != VERIFICATION_TOKEN:
        return {"status": 403}

    if "type" in json_dict:
        if json_dict["type"] == "url_verification":
            response_dict = {"challenge": json_dict["challenge"]}
            return response_dict
    return {"status": 500}

@app.route('/login', methods = ['POST', 'GET'])
def login():
    """Login URL for the admin page"""
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        if (not username or not password):
            return redirect('/login')
            
        user = API.admin.user.get_user(username)
        if (user == 'ERROR'):
            return redirect('/login')
        if (user.username and user.check_password(password)):
            session['user'] = user.username
            login_user(user)
            return redirect('/admin')
        
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')



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
    vehicle = API.db.index.get_vehicle_by_name(selected_vehicle)
    start_time, end_time = get_start_end_time_from_payload(payload)
    channel_id = payload['channel']['id']
    user_id = payload['user']['id']
    thread_id = payload['message']['ts']
    try:
        available = check_available(vehicle, start_time, end_time)
        # Schedule reservation for vehicle
        if not available:
            send_message(f"{selected_vehicle} is not available at that time", channel_id, user_id, thread_id)
        else:
            response = API.Calendar.schedule_event(vehicle.calendarGroupID, vehicle.calendarID, start_time, end_time)
            if "ERROR" in response:
                send_message(f"{response['ERROR']}", channel_id, user_id, thread_id)
            else:
                send_message(f"{selected_vehicle} was successfully reserved", channel_id, user_id, thread_id)
    except:
        send_message(f"Sorry, an error has occured, so I was unable to complete your request", channel_id, user_id, thread_id)

def check_vehicle(payload, selected_vehicle):
        vehicle = API.db.index.get_vehicle_by_name(selected_vehicle)
        start_time, end_time = get_start_end_time_from_payload(payload)
        channel_id = payload['channel']['id']
        user_id = payload['user']['id']
        thread_id = payload['message']['ts']
        try:
            available = check_available(vehicle, start_time, end_time)
            # Schedule reservation for vehicle
            if not available:
                send_message(f"{selected_vehicle} is not available at that time", channel_id, user_id, thread_id)
            else:
                send_message(f"{selected_vehicle} is available at that time", channel_id, user_id, thread_id)
        except:
            send_message(f"Sorry, an error has occured, so I was unable to complete your request", channel_id, user_id, thread_id)

def get_reservations(payload, selected_vehicle):
    vehicle = API.db.index.get_vehicle_by_name(selected_vehicle)
    channel_id = payload['channel']['id']
    user_id = payload['user']['id']
    thread_id = payload['message']['ts']
    try:
        events = API.Calendar.list_specific_calendar_in_group_events(vehicle.calendarGroupID, vehicle.calendarID)
        message = API.Calendar.pretty_print_events(events, selected_vehicle)
        send_message(message, channel_id, user_id, thread_id)
        # Schedule reservation for vehicle
    except:
        send_message(f"Sorry, an error has occured, so I was unable to complete your request", channel_id, user_id, thread_id)


@app.route('/interactions', methods = ['POST', 'GET'])
def interactions():
    if request.method == 'POST':
        data = request.form.to_dict()
        payload = json.loads(data['payload'])
        if payload['actions'][0]['action_id'] != 'submit':
            return {'status' : 200}
        else:
            selected_vehicle = get_selected_vehicle_name_from_payload(payload)
            if selected_vehicle == None:
                requests.post(payload['response_url'], json = { "text": "Did not select a vehicle"})
                return {'status': 404}
            else:
                requests.post(payload['response_url'], json = { "text": "Thanks for your request. We will process that shortly"})
            block_command_type = payload['message']['blocks'][0]['text']['text']
            if block_command_type == 'Reserve':
                reserve_vehicle(payload, selected_vehicle)
            elif block_command_type == 'Check':
                check_vehicle(payload, selected_vehicle)
            elif block_command_type == 'Reservations':
                get_reservations(payload, selected_vehicle)
            else:
                print(payload['message']['blocks'][0]['text']['text'])
            return {'status': 200}
        
def get_slack_block(path_to_file):
    vehicle_options = create_vehicle_options_slack_block()
    with open(path_to_file) as f:
        data = json.load(f)
    data['blocks'][1]['element']['options'] = vehicle_options
    with open(path_to_file, "w") as write_f:
        json.dump(data, write_f)    
    with open(path_to_file, "r") as new_f:
        new_data = json.load(new_f)
    return new_data

def create_vehicle_options_slack_block():
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
                send_message("Did not provide a command", channel_id, get_user_slack_id(), message['ts'])
                return
            command = commands[1]
            # This is where slack messages are handled
            """Makes an event on the calendar."""            
            if command.lower() == RESERVE_COMMAND:
                data = get_slack_block('slack_blocks/slack_blocks.json')        
                slack_client.chat_postMessage(channel = channel_id, thread_ts=message['ts'], text = "Please fill out the form", blocks = data['blocks'])
                                
            """Gets reservations on the calendar"""
            if command.lower() == GET_ALL_RESERVATIONS_COMMAND:
                data = get_slack_block('slack_blocks/reservations_block.json')
                slack_client.chat_postMessage(channel = channel_id, thread_ts=message['ts'], text = "Please fill out the form", blocks = data['blocks'])

            """Check if vehicle is available from start_time to end_time"""
            if command.lower() == CHECK_VEHICLE_COMMAND:    
                data = get_slack_block('slack_blocks/check_vehicle_block.json')
                slack_client.chat_postMessage(channel = channel_id, thread_ts=message['ts'], text = "Please fill out the form", blocks = data['blocks'])

            """Lists all of the vehicle's names and displays if they are available"""
            offset_minutes = 15 # 15 Minute offset for check availability. NOTE this variable is outside the scope so that way the help command can use it
            if command.lower() == VEHICLES_COMMAND:
                response_text = ""
                start_time = strftime("%Y-%m-%dT%H:%M:%S")
                
                offset_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S') + timedelta(minutes=offset_minutes)
                end_time = offset_time.strftime('%Y-%m-%dT%H:%M:%S')
                with app.app_context():
                    for vehicle in API.db.index.get_all_vehicles():
                        available = check_available(vehicle, start_time, end_time)
                        availablity_message = "available" if available else "not available"
                        response_text += f"{vehicle.name} - {availablity_message}\n"
                slack_client.chat_postMessage(text=response_text, channel=channel_id, thread_ts=message['ts'] )
            
            if command.lower() == HELP_COMMAND:
                response_text = f""" Usage Manual
                Command 1 - reserve
                Command used to reserve a vehicle.

                Command 2 - reservations
                Gets the events/reservations of a specific vehicle for today

                Command 3 - vehicles
                Lists all of the vehicles and checks if they are available in the next {offset_minutes} minutes

                Command 4 - check  
                Checks if a vehicle is available from start-time to end-time
                """
                slack_client.chat_postMessage(text=response_text, channel=channel_id, thread_ts=message['ts'] )
        
    thread = Thread(target=send_reply, kwargs={"value": event_data})
    thread.start()
    return Response(status=200)

def get_user_slack_id():
    return user_client.users_identity()['user']['id'] 

def send_direct_message(response_text):
    user_slack_id = get_user_slack_id()
    slack_client.chat_postEphemeral(channel=user_slack_id, text=response_text, user=user_slack_id)

def send_message(text, channel_id, user_id, ts_id):
    slack_client.chat_postEphemeral(channel=channel_id, text=text, user=user_id, thread_ts=ts_id)


if __name__ == "__main__":
    app.run(port=3000)