from flask import g, render_template, request, Markup

from login import requirelogin
from zoodb import *
from debug import *
import bank


@catch_err
@requirelogin
# function to validate username (alphanumeric, 128 characters or less)
def validate_username(username):
    if username is None:
        return False
    if not username.isalnum():
        return False
    if len(username) > 128:
        return False
    return True


def users():
    args = {}
    userParameter = request.args.get('user', '')
    args['req_user'] = ''
    if 'user' in request.values:
        if not validate_username(userParameter):
            args['warning'] = "Username must be alphanumeric and less than 128 characters."
            return render_template('users.html', **args)
        args['req_user'] = Markup(userParameter)
        persondb = person_setup()
        user = persondb.query(Person).get(request.values['user'])
        if user:
            p = user.profile

            p_markup = Markup("<b>%s</b>" % p)
            args['profile'] = p_markup

            args['user'] = user
            args['user_zoobars'] = bank.balance(user.username)
            args['transfers'] = bank.get_log(user.username)
        else:
            args['warning'] = "Cannot find that user."
    return render_template('users.html', **args)
