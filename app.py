import os
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
from dotenv import load_dotenv
load_dotenv()
# Local Imports
import API.Calendar
import API.admin.user
from models import Vehicle, User
from models import db

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
if (len(User.query.all()) == 0):
    admin = User('admin')
    admin.set_password('password')
    db.session.add(admin)
    db.session.commit()


migrate = Migrate(app, db)
app.config['SECRET_KEY'] = 'f9b56900692ec651739de1b4638bd091'
app.debug = True
toolbar = DebugToolbarExtension(app) # tool bar only works when app.debug is True
login = LoginManager(app)


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class MyModelView(ModelView):
    """Overide's flask_admin ModelView so that way it only displays if you are authenticated to see it"""
    def is_accessible(self):
        return current_user.is_authenticated
    
# Creates Admin Page
app.config['FLASK_ADMIN_SWATCH'] = 'darkly'
admin = Admin(app, name='Vehicle Reservation', template_mode='bootstrap3')
admin.add_view(MyModelView(Vehicle, db.session))
admin.add_view(MyModelView(User, db.session))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
slack_token = os.getenv('SLACK_BOT_TOKEN')
user_token = os.getenv('SLACK_USER_TOKEN')
VERIFICATION_TOKEN = os.getenv('VERIFICATION_TOKEN')

#instantiating slack client
slack_client = WebClient(slack_token)    
user_client = WebClient(user_token)


vehicleNames = []
for vehicle in Vehicle.query.all():
    vehicleNames.append(vehicle.name)
 

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
            
        user = API.admin.user.getUser(username)
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

def createDataDict(data):
    """ Takes in the command the user inputs into slack and returns a dictionary that contains the commands they used
    
        Keyword arguments\n
        data    -- The commands the user inputed
    """
    dataDict = {}
    # If user provided too much or too little information return dictionary containing error message
    if (len(data) != 7): 
        dataDict['Error'] = "ERROR : Did not provide correct information"        
        return dataDict
    for item in range(1, len(data), 2):
        dataDict[data[item]] = data[item+1]
    return dataDict

def getUserSlackId():
    app.client.users_identity

def checkAvailable(vehicle, startTime, endTime):
    available = API.Calendar.checkIfReservationAvailable(vehicle.calendarGroupID, vehicle.calendarID, startTime, endTime)
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
            user_id = message['user']
            commands = message.get('text').split()
            command = commands[1]
            channel_id = message["channel"]
            # This is where slack messages are handled
            """Makes an event on the calendar. INPUT FORMAT : reserve {vehicle} from {startTime} to {endTime}
            
                Example - reserve vehicle from 2022-06-15T15:00:00 to 2022-06-15T16:00:00
            """            
            if command.lower() == 'reserve':
                data = createDataDict(commands)
                if "Error" in data:
                    message = f"{data['Error']}"
                else:                
                    vehicleName = data['reserve']
                    if vehicleName not in vehicleNames:
                        message = ("Error : Did not provide a valid vehicle name")
                    else:
                        with app.app_context():
                            vehicle = Vehicle.query.filter(Vehicle.name == vehicleName).first()
                            # First check that vehicle is available
                            available = checkAvailable(vehicle, data['from'], data['to'])
                            # Schedule reservation for vehicle
                            if not available:
                                message = f"{data['reserve']} is reserved at that time!"
                            else:
                                API.Calendar.scheduleEvent(vehicle.calendarGroupID, vehicle.calendarID, data['from'], data['to'])
                                message = (  
                                    f"Reserved {data['reserve']} for <@{message['user']}> from {data['from']} to {data['to']}"
                                )
                slack_client.chat_postMessage(channel=channel_id, text=message)
            """Gets Events on the calendar"""
            if command.lower() == 'events':
                if len(commands) != 4:
                    message = (f"Error : Did not provide correct amount of information")
                else:
                    vehicleName = commands[3]
                    if vehicleName not in vehicleNames:
                        message = ("Error : Did not provide a valid vehicle name")
                    else:
                        with app.app_context():
                            vehicle = Vehicle.query.filter(Vehicle.name == vehicleName).first()
                            events = API.Calendar.listSpecificCalendarInGroupEvents(vehicle.calendarGroupID, vehicle.calendarID)
                            message = API.Calendar.prettyPrintEvents(events, vehicleName)
                slack_client.chat_postMessage(channel=channel_id, text=message)
            """Lists all of the vehicle's names"""
            if command.lower() == 'vehicles':
                message = ""
                for vehicle in vehicleNames:
                    message += f"{vehicle}, "
                slack_client.chat_postMessage(channel=channel_id, text=message)
            if command.lower() == 'help':
                message = """ Usage Manual
                Command 1  
                reserve : Command used to reserve a vehicle.
                Usage : 'reserve vehicle_name from [2022-06-15T15:00:00] to 2022-06-15T16:00:00'
                Replace the vehicle with the vehicle you would like to reserve, and the time with the correct time.

                Command 2
                events : Gets the events/reservations of a specific vehicle for today
                Usage : 'events for vehicle_name'

                Command 3
                vehicles : Lists all of the vehicles
                Usage : 'vehicles'
                """
                slack_client.chat_postMessage(channel = channel_id, text = message)
        
    thread = Thread(target=send_reply, kwargs={"value": event_data})
    thread.start()
    return Response(status=200)

def getUserSlackId():
    return user_client.users_identity()['user']['id'] 

def sendDirectMessage(message):
    user_slack_id = getUserSlackId()
    slack_client.chat_postMessage(channel=user_slack_id, text=message)

if __name__ == "__main__":
    getUserSlackId()
    app.run(port=3000)