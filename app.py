from time import strftime
from datetime import datetime, timedelta
from urllib import request
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

def create_data_dict(data):
    """ Takes in the command the user inputs into slack and returns a dictionary that contains the commands they used
    
        Keyword arguments\n
        data    -- The commands the user inputed
    """
    data_dict = {}
    # If user provided too much or too little information return dictionary containing error message
    if (len(data) != 9): 
        data_dict['Error'] = "ERROR : Did not provide correct information"        
        return data_dict
    data_dict[data[1]] = data[2]
    for item in range(3, len(data), 3):
        data_dict[data[item]] = data[item+1] + "T" + data[item+2]
    return data_dict

def checkAvailable(vehicle, start_time, end_time):
    available = API.Calendar.check_if_reservation_available(vehicle.calendarGroupID, vehicle.calendarID, start_time, end_time)
    return available


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
            command = commands[1]
            channel_id = message["channel"]
            # This is where slack messages are handled            
            """Makes an event on the calendar. INPUT FORMAT : reserve {vehicle} from {start_time} to {end_time}
            
                Example - reserve vehicle from 2022-06-15T15:00:00 to 2022-06-15T16:00:00
            """            
            if command.lower() == RESERVE_COMMAND:
                data = create_data_dict(commands)
                if "Error" in data:
                    response_text = f"{data['Error']}"
                else:                
                    vehicle_name = data['reserve']
                    similar_vehicle_names = []
                    for vehicle in vehicle_names:
                        if vehicle.startswith(vehicle_name):
                            similar_vehicle_names.append(vehicle)
                    if vehicle_name not in vehicle_names and similar_vehicle_names == []:
                        response_text = ("Error : Did not provide a valid vehicle name")
                    else:
                        with app.app_context():
                            error_occured = False
                            reserved = False
                            for vehicles in similar_vehicle_names:
                                if reserved and not error_occured:
                                    break
                                elif not reserved and not error_occured:
                                    vehicle = API.db.index.get_vehicle_by_name(vehicles)
                                    try:
                                        available = checkAvailable(vehicle, data['from'], data['to'])
                                        # Schedule reservation for vehicle
                                        if not available:
                                            response_text = f"{vehicle_name} is reserved at that time!"
                                        else:
                                            response = API.Calendar.schedule_event(vehicle.calendarGroupID, vehicle.calendarID, data['from'], data['to'])
                                            if "ERROR" in response:
                                                response_text = response['ERROR']
                                                continue
                                                
                                            else:
                                                response_text = (f"Reserved {vehicle.name} for <@{message['user']}> from {data['from']} to {data['to']}")
                                                reserved = True
                                    except:
                                        error_occured = True
                                        response_text = 'An error has occured when trying to complete your request'
                                else:
                                    break

                                
                slack_client.chat_postMessage(channel=channel_id, text=response_text, thread_ts=message['ts'])
            
            """Gets reservations on the calendar"""
            if command.lower() == GET_ALL_RESERVATIONS_COMMAND:
                if len(commands) != 4:
                    response_text = (f"Error : Did not provide correct amount of information")
                else:
                    vehicle_name = commands[3]
                    if vehicle_name not in vehicle_names:
                        response_text = ("Error : Did not provide a valid vehicle name")
                    else:
                        with app.app_context():
                            vehicle = API.db.index.get_vehicle_by_name(vehicle_name)
                            # try:
                            events = API.Calendar.list_specific_calendar_in_group_events(vehicle.calendarGroupID, vehicle.calendarID)
                            response_text = API.Calendar.pretty_print_events(events, vehicle_name)
                            # except:
                            #     response_text = 'An error has occured when trying to complete your request'
                slack_client.chat_postMessage(channel=channel_id, thread_ts=message['ts'], text=response_text)
            
            """Lists all of the vehicle's names and displays if they are available"""
            if command.lower() == VEHICLES_COMMAND:
                response_text = ""
                start_time = strftime("%Y-%m-%dT%H:%M:%S")
                offset_minutes = 15 # 15 Minute offset for check availability
                offset_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S') + timedelta(minutes=offset_minutes)
                end_time = offset_time.strftime('%Y-%m-%dT%H:%M:%S')
                with app.app_context():
                    for vehicle in API.db.index.get_all_vehicles():
                        available = checkAvailable(vehicle, start_time, end_time)
                        availablity_message = "available" if available else "not available"
                        response_text += f"{vehicle.name} - {availablity_message}\n"
                slack_client.chat_postMessage(channel=channel_id, thread_ts=message['ts'], text=response_text)
            
            """Check if vehicle is available from start_time to end_time
               Format : check {vehicle_name} from {start_time} to {end_time}
            """
            if command.lower() == CHECK_VEHICLE_COMMAND:
                data = create_data_dict(commands)
                if "Error" in data:
                    response_text = (f"Error : Did not provide correct amount of information")
                else:
                    vehicle_name = data["check"]
                    if vehicle_name not in vehicle_names:
                        response_text = (f"Error : Did not provide a valid vehicle name : {vehicle_name}")
                    else:
                        with app.app_context():
                            vehicle = API.db.index.get_vehicle_by_name(vehicle_name)
                            start_time = data['from']
                            end_time = data['to']
                            
                            try:
                                available = checkAvailable(vehicle, start_time, end_time)
                                available_message = 'available' if available else 'not available'
                                response_text = f'{vehicle_name} is {available_message}'
                            except:
                                response_text = 'An error has occured when trying to complete your request'
                slack_client.chat_postMessage(channel=channel_id, thread_ts=message['ts'], text=response_text)

            if command.lower() == HELP_COMMAND:
                response_text = """ Usage Manual
                Command 1 - reserve
                Command used to reserve a vehicle.
                USAGE : reserve vehicle_name from start_time to end_time
                EXAMPLE : reserve golf-cart-1 from 2022-06-15 15:00:00 to 2022-06-15 16:00:00

                Command 2 - reservations
                Gets the events/reservations of a specific vehicle for today
                USAGE : 'events for vehicle_name'

                Command 3 - vehicles
                Lists all of the vehicles
                USAGE : 'vehicles'

                Command 4 - check  
                Checks if a vehicle is available from start-time to end-time
                USAGE : check vehicle_name from start_time to end_time
                EXAMPLE : check golf-cart-1 from 2022-06-22T08:00:00 to 2022-06-22T09:00:00
                """
                slack_client.chat_postMessage(channel = channel_id, thread_ts=message['ts'], text = response_text)
            # if command.lower() == "test":
            #     review_message = [
            #         {
            #         "type": "section",
            #         "text": {
            #             "type": "mrkdwn",
            #             "text": "Danny Torrence left the following review for your property:"
            #         }
            #         }
            #     ]
            #     slack_client.chat_postMessage(channel = channel_id, thread_ts=message['ts'], text ="Please fill out the form", blocks = review_message)
        
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