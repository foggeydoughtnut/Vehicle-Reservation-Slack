from threading import Thread
# Flask Imports
from flask import Flask, Response, render_template
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user
# Slack Imports
from slackeventsapi import SlackEventAdapter
# Local Imports
import api.Calendar # Don't delete this. For some reason when deleted, there is a circular import
from app.models import Vehicle, User
from app.models import db
from config import SLACK_SIGNING_SECRET
import api.db.index
from app.views import login, logout, create_new_user, interactions, event_hook
from app.links import links
from app.slack_bot import SlackBotLogic

# This function is required or else there will be a context error
def create_app():
    new_app = Flask(__name__, template_folder='./app/templates', static_folder='./app/static')
    new_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    new_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(new_app)

    # Add views
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
    return render_template('404.html', admin_route=links.admin_home), 404
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
        return self.render('user_create.html', create_new_user_route=links.create_new_user)


class MyHomeView(AdminIndexView):
    @expose(links.home)
    def index(self):
        text = 'Log In' if not current_user.is_authenticated else 'Log Out'
        return self.render('admin/index.html', button_text=text, logout_route=links.logout)


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
slack_events_adapter = SlackEventAdapter(
    SLACK_SIGNING_SECRET, "/slack/events", app
)
slack_bot = SlackBotLogic()


@slack_events_adapter.on("app_mention")
def handle_message(event_data):
    def send_reply(value):
        slack_bot.handle_message_response(value, app)

    thread = Thread(target=send_reply, kwargs={"value": event_data})
    thread.start()
    return Response(status=200)


if __name__ == "__main__":
    app.run(port=3000)
