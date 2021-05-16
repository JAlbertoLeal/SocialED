# -*- coding: iso-8859-15 -*-


from flask import Flask, request, render_template, session, redirect, url_for
import os.path
from os import listdir
import json
from time import time
import sys

app = Flask(__name__)

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))


@app.route('/', methods=['GET'])

@app.route('/index.html', methods=['GET'])
def index():
    """
    Procesa '/' y '/index' urls.
    :return: contenido index.html
    """
    if 'user_name' in session:
        logged = True
        nickname = session['user_name']
    else:
        logged = False
        nickname = ''
    return render_template('index.html', logged=logged, nickname=nickname)


# este codigo controla los errores de campos ausentes
def process_missingFields(campos, next_page):
    """
    :param campos: Lista de Campos que faltan
    :param next_page: ruta al pulsar botón continuar
    :return: plantilla generada
    """
    return render_template("missingFields.html", inputs=campos, next=next_page)


@app.route('/home.html', methods=['GET'])
def home():
    return render_template("home.html")

@app.route('/login.html', methods=['GET'])
def login():
    return render_template("login.html")


@app.route('/signup.html', methods=['GET', 'POST'])
def signup():
    """
    '/signup' url (crear un usuario nuevo)
    :return: Primero renderiza la página vacia. Después los datos.
    """
    if request.method == 'POST':
        return process_signup()

    # The http GET method was used
    return app.send_static_file('signup.html')


@app.route('/processLogin', methods=['GET', 'POST'])
def processLogin():
       missing = []
       fields = ['email', 'passwd', 'login_submit']
       for field in fields:
              value = request.form.get(field, None)
              if value is None:
                  missing.append(field)
       if missing:
              return process_missingFields(missing, "/login.html")


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


@app.route('/processSignup', methods=['GET', 'POST'])
def processSignup():
       missing = []
       fields = ['nickname', 'email', 'passwd','confirm', 'signup_submit']
       for field in fields:
              value = request.form.get(field, None)
              if value is None:
                     missing.append(field)
       if missing:
              return process_missingFields(missing, "/signup.html")

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


@app.route('/processHome', methods=['GET', 'POST'])
def processHome():
	missing = []
	fields = ['message', 'last', 'post_submit']
	for field in fields:
		value = request.form.get(field, None)
		if value is None:
			missing.append(field)
	if missing:
		return process_missingFields(missing, "/home.html")

	return '<!DOCTYPE html> ' \
           '<html lang="es">' \
           '<head>' \
           '<link href="static/css/socialed-style.css" rel="stylesheet" type="text/css"/>' \
           '<title> Inicio - SocialED </title>' \
           '</head>' \
           '<body> <div id="container">' \
		   '<a href="/"> SocialED </a> | <a href="home"> Home </a> | <a href="login"> Log In </a> | <a href="signup"> Sign Up </a>' \
           '<h1>Hi, How are you?</h1>' \
                	'<form action="processHome" method="post" name="home"> ' \
			'<label for="message">Say something:</label><div class="inputs">' \
			'<input id="message" maxlength="128" name="message" size="80" type="text" required="true" value=""/>' \
			'<input id="last" type="hidden" name="last" required="true" value="' + request.form['last'] + '<br>'+ request.form['message'] + '">' \
	                 '</div>' \
                    	'<div class="inputs">' \
                        '<input id="post_submit" name="post_submit" type="submit" value="Post!"/>' \
           		'<br><br>Previous Posts: <br>' + request.form['last'] + '<br>' +request.form['message'] + \
                	'</form>' \
            		'</div></div>' \
           '</body>' \
           '</html>'


def process_signup():
    faltan = []
    campos = ['nickname', 'email', 'passwd', 'confirm', 'signup_submit']
    for campo in campos:
        value = request.form.get(campo, None)
        if value is None or value == '':
            faltan.append(campo)
    if faltan:
        return render_template("missingFields.html", inputs=faltan, next=url_for("signup"))
    return create_user_file(request.form['nickname'], request.form['email'], request.form['passwd'],
                            request.form['confirm'])

def process_error(message, next_page):
    """

    :param message:
    :param next_page:
    :return:
    """
    return render_template("error.html", error_message=message, next=next_page)


def load_user(email, passwd):
    """
    Carga usuarios.
    Comprueba que coincide el email
    :param email: user id
    :param passwd: password
    :return: pagina inicio  si el usuario existe y el pass es correcto
    """
    file_path = os.path.join(SITE_ROOT, "data/", email)
    if not os.path.isfile(file_path):
        return process_error("User not found / No existe un usuario con ese nombre", url_for("login"))
    with open(file_path, 'r') as f:
        data = json.load(f)
    if data['password'] != passwd:
        return process_error("Incorrect password / la clave no es correcta", url_for("login"))
    session['user_name'] = data['user_name']
    session['messages'] = data['messages']
    session['password'] = passwd
    session['email'] = email
    session['friends'] = data['friends']
    return redirect(url_for("home"))

def save_current_user():
    datos = {
        "user_name": session["user_name"],
        "password": session['password'],
        "messages": session['messages'],  # lista de tuplas (time_stamp, mensaje)
        "email": session['email'],
        "friends": session['friends']
    }
    file_path = os.path.join(SITE_ROOT, "data/", session['email'])
    with open(file_path, 'w') as f:
        json.dump(datos, f)


def create_user_file(name, email, passwd, passwd_confirmation):
    """
    Crea el fichero (en /data ) el nombre del fichero es email.
    Si ya existe el fichero error.
    Si no coincide el pass error.
    :param name: Nombre o nickname del usuario
    :param email: correo, luego se usa para almacenar datos
    :param passwd: password
    :param passwd_confirmation: repite el pass
    :return: Si no hay errores, muestra la pagina home
    """

    directory = os.path.join(SITE_ROOT, "data")
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(SITE_ROOT, "data/", email)
    if os.path.isfile(file_path):
        return process_error(
            "The email is already used, you must select a different email / Ya existe un usuario con ese nombre",
            url_for("signup"))
    if passwd != passwd_confirmation:
        return process_error("Your password and confirmation password do not match / Las claves no coinciden",
                             url_for("signup"))
    datos = {
        "user_name": name,
        "password": passwd,
        "messages": [],
        "friends": []
    }
    with open(file_path, 'w') as f:
        json.dump(datos, f)
    session['user_name'] = name
    session['password'] = passwd
    session['messages'] = []
    session['friends'] = []
    session['email'] = email
    return redirect(url_for("home"))


def get_friends_messages_with_authors():
    """
    Obtiene los mensajes de los amigos  (del usuario de la sesión)
    :return: Lista de mensajes, formato (usuario, marca tiempo, mensaje)
    """
    message_and_authors = []
    for friend in session['friends']:
        texts = load_messages_from_user(friend)
        message_and_authors.extend(texts)
    return message_and_authors


def load_messages_from_user(user):
    """
    Obtiene todos los mensajes de un usuario
    :param user: el usuario
    :return: todos los mensajes publicados, formato (usuario, marca tiempo, mensaje)
    """
    file_path = os.path.join(SITE_ROOT, "data/", user)
    if not os.path.isfile(file_path):
        return []
    with open(file_path, 'r') as f:
        data = json.load(f)
    messages_with_author = [(data["user_name"], message[0], message[1]) for message in data["messages"]]
    return messages_with_author


def get_all_users(user):
    """
    Obtienes los amigos de un usuario (parameter)
    :param user: usuario actual
    :return: Lista de usuarios amigos del usuario actual
    """
    dir_path = os.path.join(SITE_ROOT, "data/")
    user_list = listdir(dir_path)
    user_list.remove(user)
    return user_list

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True, port=55555)