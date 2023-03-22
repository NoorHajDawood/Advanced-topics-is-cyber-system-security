from flask import g, render_template, request, Markup

from login import requirelogin
from zoodb import *
from debug import *
import bank

@catch_err
@requirelogin

# function to validate user input from html injections and sql injections:
def validate_input(input):
    if input is None:
        return False
    if len(input) > 20:
        return False
    if input == "":
        return False
    if input[0] == " ":
        return False
    if input[-1] == " ":
        return False
    if input[0] == "-":
        return False
    if input[-1] == "-":
        return False
    if input[0] == "_":
        return False
    if input[-1] == "_":
        return False
    if input[0] == ".":
        return False
    if input[-1] == ".":
        return False
    if input[0] == "/":
        return False
    if input[-1] == "/":
        return False
    if input[0] == "\\":
        return False
    if input[-1] == "\\":
        return False
    if input[0] == "*":
        return False
    if input[-1] == "*":
        return False
    if input[0] == "(":
        return False
    if input[-1] == "(":
        return False
    if input[0] == ")":
        return False
    if input[-1] == ")":
        return False
    if input[0] == "[":
        return False
    if input[-1] == "[":
        return False
    if input[0] == "]":
        return False
    if input[-1] == "]":
        return False
    if input[0] == "{":
        return False
    if input[-1] == "{":
        return False
    if input[0] == "}":
        return False
    if input[-1] == "}":
        return False
    if input[0] == "<":
        return False
    if input[-1] == "<":
        return False
    if input[0] == ">":
        return False
    if input[-1] == ">":
        return False
    if input[0] == "'":
        return False
    if input[-1] == "'":
        return False
    if input[0] == '"':
        return False
    if input[-1] == '"':
        return False
    if input[0] == ";":
        return False
    if input[-1] == ";":
        return False
    if input[0] == ":":
        return False
    if input[-1] == ":":
        return False
    if input[0] == ",":
        return False
    if input[-1] == ",":
        return False
    if input[0] == "?":
        return False
    if input[-1] == "?":
        return False
    if input[0] == "!":
        return False
    if input[-1] == "!":
        return False
    if input[0] == "@":
        return False
    if input[-1] == "@":
        return False
    if input[0] == "#":
        return False
    if input[-1] == "#":
        return False
    if input[0] == "$":
        return False
    if input[-1] == "$":
        return False
    if input[0] == "%":
        return False
    if input[-1] == "%":
        return False
    if input[0] == "^":
        return False
    if input[-1] == "^":
        return False
    if input[0] == "&":
        return False
    if input[-1] == "&":
        return False

    return True

def users():
    args = {}
    userParameter = request.args.get('user', '')
    if not validate_input(userParameter):
        args['warning'] = "Invalid user input"
        return render_template('users.html', **args)
    args['req_user'] = Markup(userParameter)
    if 'user' in request.values:
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
