from flask import redirect, request, render_template, session, flash
from flask_login import login_user, logout_user
import API.db.index
import requests
import json
import app
from config import VERIFICATION_TOKEN

def login():
    """Login URL for the admin page"""
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        if (not username or not password):
            return redirect('/login')
        user = API.db.index.get_user_by_username(username)
        if (user == None):
            return redirect('/login')
        if (user.username and user.check_password(password)):
            session['user'] = user.username
            login_user(user)
            return redirect('/admin')
    return render_template('login.html')

def logout():
    logout_user()
    return redirect('/login')

def create_new_user():
    if (request.method == 'POST'):
        if (request.form.get('Cancel')):
            return redirect('/admin/user/')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        password_are_same = (password == confirm_password)
        username_exists = API.db.index.check_if_user_exists(username)

        if password_are_same and not username_exists:
            API.db.index.create_user(username, password)
            flash('Successfully created account')
            return redirect('/admin/user/')
        else:
            if not password_are_same:
                flash('Passwords did not match')
                return redirect('/admin/user/new')
            elif username_exists:
                flash('That username already exists')
                return redirect('/admin/user/new')


def interactions():
    if request.method == 'POST':
        data = request.form.to_dict()
        payload = json.loads(data['payload'])
        if payload['actions'][0]['action_id'] != 'submit':
            return {'status' : 200}
        else:
            selected_vehicle = app.get_selected_vehicle_name_from_payload(payload)
            if selected_vehicle == None:
                requests.post(payload['response_url'], json = { "text": "Did not select a vehicle"})
                return {'status': 404}
            else:
                requests.post(payload['response_url'], json = { "text": "Thanks for your request. We will process that shortly"})
            block_command_type = payload['message']['blocks'][0]['text']['text']
            if block_command_type == 'Reserve':
                app.reserve_vehicle(payload, selected_vehicle)
            elif block_command_type == 'Check':
                app.check_vehicle(payload, selected_vehicle)
            elif block_command_type == 'Reservations':
                app.get_reservations(payload, selected_vehicle)
            else:
                print(payload['message']['blocks'][0]['text']['text'])
            return {'status': 200}

def event_hook(request = None):
    if request != None:
        json_dict = json.loads(request.body.decode("utf-8"))
        if json_dict["token"] != VERIFICATION_TOKEN:
            return {"status": 403}

        if "type" in json_dict:
            if json_dict["type"] == "url_verification":
                response_dict = {"challenge": json_dict["challenge"]}
                return response_dict
        return {"status": 500}
    else:
        return redirect('/login')