from zoodb import *
from debug import *
from login import logged_in
import time

def transfer(sender, recipient, zoobars):
    bankdb = bank_setup()
    senderp = bankdb.query(Bank).get(sender)
    recipientp = bankdb.query(Bank).get(recipient)

    if not senderp or not recipientp:
        return None

    # check if sender and recipient are the same
    if sender == recipient:
        return None

    # check if zoobars includes only digits and is positive
    if (not str(zoobars).isdigit()) or (int(zoobars) == 0):
        # raise ValueError()
        return None

    sender_balance = senderp.zoobars - zoobars
    recipient_balance = recipientp.zoobars + zoobars

    if sender_balance < 0 or recipient_balance < 0:
        # raise ValueError()
        return None

    senderp.zoobars = sender_balance
    recipientp.zoobars = recipient_balance
    bankdb.commit()

    transfer = Transfer()
    transfer.sender = sender
    transfer.recipient = recipient
    transfer.amount = zoobars
    transfer.time = time.asctime()

    transferdb = transfer_setup()
    transferdb.add(transfer)
    transferdb.commit()

def balance(username):
    db = bank_setup()
    bank = db.query(Bank).get(username)
    if not bank:
        return None
    return bank.zoobars

def get_log(username):
    db = transfer_setup()
    l = db.query(Transfer).filter(or_(Transfer.sender==username,
                                      Transfer.recipient==username))
    r = []
    for t in l:
       r.append({'time': t.time,
                 'sender': t.sender ,
                 'recipient': t.recipient,
                 'amount': t.amount })
    return r 

def check_in(username):
    bankdb = bank_setup()
    user = bankdb.query(Bank).get(username)
    if user:
       return
    bank = Bank()
    bank.username = username
    bankdb.add(bank)
    bankdb.commit()
