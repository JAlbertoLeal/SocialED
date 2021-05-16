# -*- coding: iso-8859-15 -*-

import json
from flask import Flask, request, render_template, session, redirect, url_for
import os.path
from os import listdir
import json
from time import time
import sys

app = Flask(__name__)

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

def process_missingFields(campos, next_page):
    return render_template("missingFields.html", inputs=campos, next=next_page)

@app.route('/', methods=['GET'])
def index():
    if 'user_name' in session:
        return render_template("index.html", logged=True, nickname=session['user_name'])
    else:
        return render_template("index.html", logged=False, nickname='')


@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html', logged=True, nickname=session['user_name'], messages=session['messages'])

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')


@app.route('/processLogin', methods=['GET', 'POST'])
def processLogin():
    missing = []
    fields = ['email', 'passwd', 'login_submit']
    for field in fields:
        value = request.form.get(field, None)
        if value is None:
            missing.append(field)
    if missing:
        return process_missingFields(missing, "/login")
    return load_user(request.form['email'], request.form['passwd'])

"""
       return '<!DOCTYPE html> ' \
           '<html lang="es">' \
           '<head>' \
           '<link href="static/css/socialed-style.css" rel="stylesheet" type="text/css"/>' \
           '<title> Home - SocNet </title>' \
           '</head>' \
           '<body> <div id ="container">' \
		   '<a href="/"> SocNet </a> | <a href="home"> Home </a> | <a href="login"> Log In </a> | <a href="signup"> Sign Up </a>' \
           '<h1>Data from Form: Login</h1>' \
	       '<form><label>email: ' + request.form['email'] + \
	       '</label><br><label>passwd: ' + request.form['passwd'] + \
           '</label></form></div></body>' \
           '</html>'
"""

@app.route('/processSignup', methods=['GET', 'POST'])
def processSignup():
    missing = []
    fields = ['nickname', 'email', 'passwd','confirm', 'signup_submit']
    for field in fields:
        value = request.form.get(field, None)
        if value is None:
            missing.append(field)
    if missing:
        return process_missingFields(missing, "/signup")
    return create_user_file(request.form['nickname'], request.form['email'], request.form['passwd'], request.form['confirm'])

"""
       return '<!DOCTYPE html> ' \
           '<html lang="es">' \
           '<head>' \
           '<link href="static/css/socialed-style.css" rel="stylesheet" type="text/css"/>' \
           '<title> Inicio - SocialED </title>' \
           '</head>' \
           '<body> <div id ="container">' \
		   '<a href="/"> SocialED </a> | <a href="home"> Home </a> | <a href="login"> Log In </a> | <a href="signup"> Sign Up </a>' \
           '<h1>Data from Form: Sign Up</h1>' \
           '<form><label>Nickame: ' + request.form['nickname'] + \
	       '</label><br><label>email: ' + request.form['email'] + \
	       '</label><br><label>passwd: ' + request.form['passwd'] + \
	       '</label><br><label>confirm: ' + request.form['confirm'] + \
           '</label></form></div></body>' \
           '</html>'
"""

@app.route('/processHome', methods=['GET', 'POST'])
def processHome():
    if 'user_name' not in session:
        return process_error("you must be logged to use the app / debe registrarse antes de usar la aplicacion", url_for("login"))

    if request.method == 'POST' and request.form['message'] !="":
        messages=session['messages']
        if not messages:
            messages=[]
        messages.append((time(), request.form['message']))
        save_current_user()
    else:
        messages=session['messages']
    session['messages']=messages
    return render_template('home.html', logged=True, nickname=session['user_name'], messages=messages)

def process_error(message, next_page):
    return render_template("error.html", error_message=message, next=next_page)

def load_user(email, passwd):
    file_path = os.path.join(SITE_ROOT, "data/", email)
    if not os.path.isfile(file_path):
        return process_error("User not found / No existe un usuario con ese nombre", url_for("login"))
    with open(file_path, 'r') as f:
        data=json.load(f)
    if data['password'] != passwd:
        return process_error("Incorrect password / La clave no es correcta", url_for("login"))
    session['user_name']=data['user_name']
    session['messages']=data['messages']
    session['password']=passwd
    session['email']=email
    session['friends']=data['friends']
    return render_template('home.html', logged=True, nickname=session['user_name'], messages=session['messages'])

def save_current_user():
    datos={
        "user_name": session["user_name"],
        "password": session['password'],
        "messages": session['messages'],
        "email": session['email'],
        "friends": session['friends']
    }
    file_path = os.path.join(SITE_ROOT, "data/", session['email'])
    with open(file_path, 'w') as f:
        json.dump(datos, f)

def create_user_file(name, email, passwd, passwd_confirmation):
    directory=os.path.join(SITE_ROOT, "data")
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path=os.path.join(SITE_ROOT, "data/", email)
    if os.path.isfile(file_path):
        return process_error("The email is already used, you must select a different email / Ya existe un usuario con ese email", url_for("signup"))
    if passwd != passwd_confirmation:
        return process_error("Your password and confirmation password do not match / Las claves no coinciden", url_for("signup"))
    datos={
        "user_name": name,
        "password": passwd,
        "messages": [],
        "friends": []
    }
    with open(file_path, 'w') as f:
        json.dump(datos, f)
    session['user_name']=name
    session['password']=passwd
    session['messages']=[]
    session['friends']=[]
    session['email']=email
    return render_template('home.html', logged=True, nickname=session['user_name'], messages=session['messages'])

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True, port=55555)