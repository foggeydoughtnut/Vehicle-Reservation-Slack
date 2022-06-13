import os
from urllib import request
# Flask Imports
from flask import Flask, Response, redirect, request, render_template, session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# Slack Imports
from slackeventsapi import SlackEventAdapter
from slack import WebClient

from threading import Thread
from dotenv import load_dotenv
load_dotenv()
# Local Imports
from API.Calendar import prettyPrintEvents, scheduleEvent, listEvents, getCalendarGroups
from models import Vehicle, User
from API.admin.user import getUser
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


# # TEMP
# print(getCalendarGroups().json()['value'][2]['id'])

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
VERIFICATION_TOKEN = os.getenv('VERIFICATION_TOKEN')

#instantiating slack client
slack_client = WebClient(slack_token)

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
            
        user = getUser(username)
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
            """Makes an event on the calendar. INPUT FORMAT : reserve {vehicle} from {startTime} to {endTime}"""            
            if command.lower() == 'reserve':
                data = createDataDict(commands)
                scheduleEvent(data['from'], data['to'])
                message = (  
                    f"Reserved {data['reserve']} for <@{message['user']}> from {data['from']} to {data['to']}" if ("Error" not in data) else f"{data['Error']}"
                )
                slack_client.chat_postMessage(channel=channel_id, text=message)
            """Gets Events on the calendar"""
            if command.lower() == 'events':
                events = listEvents()
                message = prettyPrintEvents(events)
                slack_client.chat_postMessage(channel=channel_id, text=message)
            
        
    thread = Thread(target=send_reply, kwargs={"value": event_data})
    thread.start()
    return Response(status=200)


if __name__ == "__main__":
    app.run(port=3000)