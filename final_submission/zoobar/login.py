import datetime
from flask import g, redirect, render_template, request, url_for, Markup
from functools import wraps
from debug import *
from zoodb import *

import auth_client
import bank_client
import random

class User(object):
    def __init__(self):
        self.person = None

    def checkLogin(self, username, password):
        token = auth_client.login(username, password)
        if token is not None:
            return self.loginCookie(username, token)
        else:
            return None

    def loginCookie(self, username, token):
        self.setPerson(username, token)
        return "%s#%s" % (username, token)

    def logout(self):
        self.person = None

    def addRegistration(self, username, password):
        token = auth_client.register(username, password)
        bank_client.check_in(username)
        if token is not None:
            return self.loginCookie(username, token)
        else:
            return None

    def checkCookie(self, cookie):
        if cookie is None:
            return
        try:
            (username, token) = cookie.rsplit("#", 1)
        except:
            username = ''
            token = ''
        if auth_client.check_token(username, token):
            self.setPerson(username, token)

    def setPerson(self, username, token):
        persondb = person_setup()
        self.person = persondb.query(Person).get(username)
        self.token = token
        self.zoobars = bank_client.balance(username)

    def login_attempt(self, username):
        persondb = person_setup()
        self.person = persondb.query(Person).get(username)
        if self.person is not None:
            return self.person.login_attempts
        return 0

    def login_attempt_time(self, username):
        persondb = person_setup()
        self.person = persondb.query(Person).get(username)
        if self.person is not None:
            if self.person.last_login_attempt is not None:
                return self.person.last_login_attempt
            else:
                return datetime.datetime.now()

    def checkLoginAttempts(self, username):
        if self.login_attempt(username) >= login_attempts_limit:
            if self.login_attempt_time(username) > datetime.datetime.now() - datetime.timedelta(minutes=login_time_limit):
                return False
            else:
                return True
        return True

def logged_in():
    g.user = User()
    g.user.checkCookie(request.cookies.get("PyZoobarLogin"))
    if g.user.person:
        return True
    else:
        return False

def requirelogin(page):
    @wraps(page)
    def loginhelper(*args, **kwargs):
        if not logged_in():
            return redirect(url_for('login') + "?nexturl=" + request.url)
        else:
            return page(*args, **kwargs)
    return loginhelper

# function to validate username (alphanumeric, 128 characters or less)
def validate_username(username):
    if username is None:
        return False
    if not username.isalnum():
        return False
    if len(username) > 128:
        return False
    return True

# password restrictions (8-128 characters, at least 1 number, at least 1 letter, at least 1 special character)
def validate_password(password):
    if len(password) < 8 or len(password) > 128:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    if not any(not char.isalnum() for char in password):
        return False
    return True

@catch_err
def login():
    cookie = None
    login_error = ""
    user = User()

    if request.method == 'POST':
        username = request.form.get('login_username')
        password = request.form.get('login_password')
        if not validate_username(username):
            login_error = "Username be alphanumeric and 128 characters or less. (for example, 'joe' or 'joe123')"
            return render_template('login.html', login_error=login_error)
        if 'submit_registration' in request.form:
            if not username:
                login_error = "You must supply a username to register."
            elif not password:
                login_error = "You must supply a password to register."
            elif not validate_password(password):
                login_error = "Password must be 8-128 characters, contain at least 1 number, 1 letter, and 1 special character."
                return render_template('login.html', login_error=login_error)
            else:
                cookie = user.addRegistration(username, password)
                if not cookie:
                    login_error = "Registration failed."
                    return render_template('login.html', login_error=login_error)
        elif 'submit_login' in request.form:
            if not username:
                login_error = "You must supply a username to log in."
                return render_template('login.html', login_error=login_error)
            elif not password:
                login_error = "You must supply a password to log in."
                return render_template('login.html', login_error=login_error)
        # check login attempts before logging in
        if not user.checkLoginAttempts(username):
            login_error = "Too many login attempts. Please try again later."
            return render_template('login.html', login_error=login_error)
        cookie = user.checkLogin(username, password)
        if not cookie:
            login_error = "Invalid username or password."

    nexturl = request.values.get('nexturl', url_for('index'))
    if cookie:
        response = redirect(nexturl)
        ## Be careful not to include semicolons in cookie value; see
        ## https://github.com/mitsuhiko/werkzeug/issues/226 for more
        ## details.
        response.set_cookie('PyZoobarLogin', cookie)
        return response

    return render_template('login.html',
                           nexturl=nexturl,
                           login_error=login_error,
                           login_username=Markup(request.form.get('login_username', '')))

@catch_err
def logout():
    if logged_in():
        g.user.logout()
    response = redirect(url_for('login'))
    response.set_cookie('PyZoobarLogin', '')
    return response
