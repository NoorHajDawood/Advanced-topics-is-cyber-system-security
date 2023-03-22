import datetime
from zoodb import *
from debug import *

import hashlib
import random
import os
import pbkdf2

def newtoken(db, cred):
    hashinput = "%s%.10f" % (cred.password, random.random())
    cred.token = hashlib.md5(hashinput.encode('utf-8')).hexdigest()
    db.commit()
    return cred.token

def login(username, password):
    db_person = person_setup()
    person = db_person.query(Person).get(username)
    if not person:
        return None
    # check login attempts
    if person.login_attempts >= login_attempts_limit:
        # check if last login attempt time is within the time limit
        if person.last_login_attempt > datetime.datetime.now() - datetime.timedelta(minutes=login_time_limit):
            return None
        else:
            # reset login attempts
            person.login_attempts = 0
            db_person.commit()
    # increment login attempts
    person.login_attempts += 1
    person.last_login_attempt = datetime.datetime.now()
    db_person.commit()
    db_cred = cred_setup()
    cred = db_cred.query(Cred).get(username)
    password = pbkdf2.PBKDF2(password, cred.salt).hexread(32)
    if cred.password == password:
        # reset login attempts
        person.login_attempts = 0
        db_person.commit()
        return newtoken(db_cred, cred)
    else:
        return None

def register(username, password):
    db_person = person_setup()
    person = db_person.query(Person).get(username)
    if person:
        return None
    newperson = Person()
    newperson.username = username
    db_person.add(newperson)
    db_person.commit()
    salt = os.urandom(32)
    password = pbkdf2.PBKDF2(password,salt).hexread(32) 
    db_cred = cred_setup()
    newcred = Cred()
    newcred.username = username
    newcred.password = password
    newcred.salt = salt
    db_cred.add(newcred)
    db_cred.commit()
    return newtoken(db_cred, newcred)

def check_token(username, token):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if cred and cred.token == token:
        return True
    else:
        return False

    
