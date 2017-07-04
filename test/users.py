from __future__ import division

import random
import messages
import libtest
from libtest import send_request, handle_response
import httplib
import pdb

SERVER_URL = 'localhost'
SERVER_PORT = 8000


# should move to singleton class
global_user_list = []

import string
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


class Connect(object):
    def __init__(self, server_url=SERVER_URL, server_port=SERVER_PORT):
        self.server_url = server_url
        self.server_port = server_port
        self.conn = httplib.HTTPConnection(SERVER_URL, SERVER_PORT)


class User(object):
    def __init__(self):
        self.first_name = id_generator()
        self.last_name = id_generator()
        self.username = id_generator()
        self.target = id_generator()
        self.response_mode = 'sms'
        self.msg_hdr = dict(header=dict(deviceID='DUMMY', hash='DUMMY', version=messages.APP_VERSION))
        self.global_index = len(global_user_list)
        self.connection = Connect()
        self.conn = self.connection.conn

        self.uid = 0
        self.wuid = 0

    def get_fbizcard_image(self):
        try:
            f = open(libtest.test_image_path, 'rb')
            self.cc_out = f.read().encode('base64')
        except:
            self.cc_out = None

        return self.cc_out

    def otp_check(self):
        self.reqmsg = messages.phone_check_req.copy()
        self.reqmsg['header'].update(self.msg_hdr['header'])

        self.reqmsg['sender']['username'] = self.username
        self.reqmsg['sender']['target'] = self.target
        self.reqmsg['sender']['responseMode'] = 'sms'

        send_request(self.conn, self.reqmsg)

        # Parse and dump the JSON response from server
        objs = handle_response(self.conn, self.reqmsg['header']['msgType'])
        self.response_key = objs['data'].get('challenge_key', 1234)

        # send challenge response
        self.reqmsg = messages.phone_check_resp.copy()

        self.reqmsg['header'].update(self.msg_hdr['header'])
        self.reqmsg['sender']['username'] = self.username
        self.reqmsg['sender']['responseKey'] = self.response_key

        send_request(self.conn, self.reqmsg)
        objs = handle_response(self.conn, self.reqmsg['header']['msgType'])
        self.uid = objs['data']['userID']

        self.key = str(self.global_index)
        global_user_list.append({self.key:dict(uid=self.uid)})

    def login(self):
        self.reqmsg = messages.login.copy()
        self.reqmsg['header'].update(self.msg_hdr['header'])

        self.reqmsg['sender']['userID'] = self.uid
        self.reqmsg['sender']['username'] = self.username

        send_request(self.conn, self.reqmsg)
        objs = handle_response(self.conn, self.reqmsg['header']['msgType'])

        self.wuid = objs['data']['wizUserID']

        global_user_list[self.global_index][self.key].update(wuid=self.wuid)

    def register(self):
        self.reqmsg = messages.register1.copy()
        self.reqmsg['header'].update(self.msg_hdr['header'])

        self.reqmsg['sender']['userID'] = self.uid
        self.reqmsg['sender']['wizUserID'] = self.wuid

        send_request(self.conn, self.reqmsg)
        objs = handle_response(self.conn, self.reqmsg['header']['msgType'])

    def add_wizcard(self):
        self.reqmsg = messages.edit_card.copy()
        self.reqmsg['header'].update(self.msg_hdr['header'])

        self.reqmsg['sender']['user_id'] = self.uid
        self.reqmsg['sender']['wizuser_id'] = self.wuid

        send_request(self.conn, self.reqmsg)
        objs = handle_response(self.conn, self.reqmsg['header']['msgType'])

        self.wc_id = objs['data']['wizCardID']
        global_user_list[self.global_index][self.key].update(wc_id=self.wc_id)

    def get_cards(self):
        self.reqmsg = messages.get_cards.copy()
        self.reqmsg['header'].update(self.msg_hdr['header'])

        self.reqmsg['sender']['user_id'] = self.uid
        self.reqmsg['sender']['wizuser_id'] = self.wuid

        send_request(self.conn, self.reqmsg)
        objs = handle_response(self.conn, self.reqmsg['header']['msg_type'])

    def onboard_user(self):
        self.otp_check()
        self.login()
        self.register()
        self.add_wizcard()
        self.get_cards()

from threading import Timer
import time
import sys

def main():
    num_users = int(sys.argv[1])

    list_u = []
    for u in range(num_users):
        u = User()
        u.onboard_user()
        list_u.append(u)

    while True:
        for u in list_u:
            Timer(60, u.get_cards())

        time.sleep(60)

if __name__ == '__main__':

    main()
