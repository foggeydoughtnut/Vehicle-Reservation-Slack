from flask import redirect, request, render_template, session, flash
from flask_login import login_user, logout_user
import api.db.index
import requests
import json
from app.slack_bot import Slack_Bot_Logic
import run
from config import VERIFICATION_TOKEN
from app.links import links


def login():
    """Login URL for the admin page"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Invalid Credentials. Please try again', 'error')
            return redirect(links.login)
        user = api.db.index.get_user_by_username(username)
        if user is None:
            flash('Invalid Credentials. Please try again', 'error')
            return redirect(links.login)
        if user.username and user.check_password(password):
            session['user'] = user.username
            login_user(user)
            return redirect(links.admin_home)
        else:
            flash('Invalid Credentials. Please try again', 'error')
            return redirect(links.login)
    return render_template('login.html')


def logout():
    logout_user()
    flash('Successfully logged out', 'message')
    return redirect(links.login)


def create_new_user():
    """Route to create a new user for the admin page"""
    if request.method == 'POST':
        if request.form.get('Cancel'):
            return redirect(links.admin_user)
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        password_are_same = (password == confirm_password)
        username_exists = api.db.index.check_if_user_exists(username)

        if password_are_same and not username_exists:
            api.db.index.create_user(username, password)
            flash('Successfully created account', 'success')
            return redirect(links.admin_user)
        else:
            if not password_are_same:
                flash('Passwords did not match', 'error')
                return redirect(links.admin_user_new)
            elif username_exists:
                flash('That username already exists', 'error')
                return redirect(links.admin_user_new)


def interactions():
    """The route that slack blocks call when you click submit"""
    slack_bot = Slack_Bot_Logic()
    if request.method == 'POST':
        data = request.form.to_dict()
        payload = json.loads(data['payload'])
        if payload['actions'][0]['action_id'] != 'submit':
            return {'status': 200}
        else:
            selected_vehicle = Slack_Bot_Logic.get_selected_vehicle_name_from_payload(payload)
            if selected_vehicle is None:
                requests.post(payload['response_url'], json={"text": "Did not select a vehicle"})
                return {'status': 404}
            else:
                requests.post(payload['response_url'],
                              json={"text": "Thanks for your request. We will process that shortly"})
            block_command_type = payload['message']['blocks'][0]['text']['text']
            if block_command_type == 'Reserve':
                run.reserve_vehicle(payload, selected_vehicle)
            elif block_command_type == 'Check':
                run.check_vehicle(payload, selected_vehicle)
            elif block_command_type == 'Reservations':
                slack_bot.get_reservations(payload, selected_vehicle)
            else:
                print(payload['message']['blocks'][0]['text']['text'])
            return {'status': 200}


def event_hook(request=None):
    """The base url route. Needed for the request url verification for slack"""
    if request is not None:
        json_dict = json.loads(request.body.decode("utf-8"))
        if json_dict["token"] != VERIFICATION_TOKEN:
            return {"status": 403}

        if "type" in json_dict:
            if json_dict["type"] == "url_verification":
                response_dict = {"challenge": json_dict["challenge"]}
                return response_dict
        return {"status": 500}
    else:
        return redirect(links.login)
