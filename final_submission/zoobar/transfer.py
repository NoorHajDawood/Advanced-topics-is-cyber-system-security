from flask import g, render_template, request

from login import requirelogin
from zoodb import *
from debug import *
import bank_client
import traceback

# function to validate username (alphanumeric, 128 characters or less)


def validate_username(username):
    if username is None:
        return False
    if not username.isalnum():
        return False
    if len(username) > 128:
        return False
    return True


@catch_err
@requirelogin
def transfer():
    warning = None
    try:
        if 'recipient' in request.form:
            # check if zoobars includes only digits and is positive
            if (not request.form['zoobars'].isdigit()) or (int(request.form['zoobars']) == 0):
                warning = "Zoobars must be a positive number"
                return render_template('transfer.html', warning=warning)
            zoobars = eval(request.form['zoobars'])
            if not validate_username(request.form['recipient']):
                warning = "Username must be alphanumeric and less than 128 characters."
                return render_template('transfer.html', warning=warning)
            if bank_client.transfer(g.user.person.username,
                                    request.form['recipient'], zoobars) is None:
                warning = "Transfer to %s failed" % request.form['recipient']
            else:
                warning = "Sent %d zoobars" % zoobars
    except (KeyError, ValueError, AttributeError) as e:
        traceback.print_exc()
        warning = "Transfer to %s failed" % request.form['recipient']

    return render_template('transfer.html', warning=warning)
