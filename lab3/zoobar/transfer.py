from flask import g, render_template, request

from login import requirelogin
from zoodb import *
from debug import *
import bank_client
import traceback

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
            if bank_client.transfer(g.user.person.username,
                          request.form['recipient'], zoobars) is None:
                warning = "Transfer to %s failed" % request.form['recipient']
            else:
                warning = "Sent %d zoobars" % zoobars
    except (KeyError, ValueError, AttributeError) as e:
        traceback.print_exc()
        warning = "Transfer to %s failed" % request.form['recipient']

    return render_template('transfer.html', warning=warning)
