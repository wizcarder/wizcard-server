from __future__ import division

import random
import messages
import libtest
from libtest import send_request, handle_response
import httplib
import pdb
from random import sample

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
        self.device_id = "DUMMY_DEVICE_ID"
        self.response_mode = 'sms'
        self.msg_hdr = dict(header=dict(device_id=self.device_id, hash='DUMMY', version=messages.APP_VERSION))
        self.global_index = len(global_user_list)
        self.connection = Connect()
        self.conn = self.connection.conn

        self.uid = 0
        self.wuid = 0

    def password(self, uid):
        return self.device_id+uid

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
        self.reqmsg['sender']['response_mode'] = 'sms'

        send_request(self.conn, self.reqmsg)

        # Parse and dump the JSON response from server
        objs = handle_response(self.conn, self.reqmsg['header']['msg_type'])
        self.response_key = objs['data'].get('challenge_key', 1234)

        # send challenge response
        self.reqmsg = messages.phone_check_resp.copy()

        self.reqmsg['header'].update(self.msg_hdr['header'])
        self.reqmsg['sender']['username'] = self.username
        self.reqmsg['sender']['response_key'] = self.response_key

        send_request(self.conn, self.reqmsg)
        objs = handle_response(self.conn, self.reqmsg['header']['msg_type'])
        self.uid = objs['data']['user_id']

        self.key = str(self.global_index)
        global_user_list.append({self.key:dict(uid=self.uid)})

    def login(self):
        self.reqmsg = messages.login.copy()
        self.reqmsg['header'].update(self.msg_hdr['header'])

        self.reqmsg['sender']['user_id'] = self.uid
        self.reqmsg['sender']['username'] = self.username
        self.reqmsg['sender']['password'] = self.password(self.uid)

        send_request(self.conn, self.reqmsg)
        objs = handle_response(self.conn, self.reqmsg['header']['msg_type'])

        self.wuid = objs['data']['wizuser_id']

        global_user_list[self.global_index][self.key].update(wuid=self.wuid)

    def register(self):
        self.reqmsg = messages.register1.copy()
        self.reqmsg['header'].update(self.msg_hdr['header'])

        self.reqmsg['sender']['user_id'] = self.uid
        self.reqmsg['sender']['wizuser_id'] = self.wuid

        send_request(self.conn, self.reqmsg)
        objs = handle_response(self.conn, self.reqmsg['header']['msg_type'])

    def add_wizcard(self):
        self.reqmsg = messages.edit_card.copy()
        self.reqmsg['header'].update(self.msg_hdr['header'])

        self.reqmsg['sender']['user_id'] = self.uid
        self.reqmsg['sender']['wizuser_id'] = self.wuid

        send_request(self.conn, self.reqmsg)
        objs = handle_response(self.conn, self.reqmsg['header']['msg_type'])

        self.wc_id = objs['data']['wizcard']['wizcard_id']
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

    def send_asset_to_xyz(self, users):
        valid_users = []
        for u in users:
            if self.uid != u.uid:
                valid_users.append(u.wuid)

        self.reqmsg = messages.send_asset_to_xyz.copy()
        self.reqmsg['header'].update(self.msg_hdr['header'])

        self.reqmsg['sender']['user_id'] = self.uid
        self.reqmsg['sender']['wizuser_id'] = self.wuid
        self.reqmsg['sender']['asset_id'] = self.wc_id
        self.reqmsg['sender']['asset_type'] = "wizcard"
        self.reqmsg['receiver']['receiver_type'] = "wiz_untrusted"
        self.reqmsg['receiver']['receiver_ids'] = valid_users
        send_request(self.conn, self.reqmsg)
        objs = handle_response(self.conn, self.reqmsg['header']['msg_type'])



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

    # AA: commenting all this. No point doing it like a test/register manner all over again.
    # this needs to be done in a better, structured manner. where there is a test.definition and the stuff
    # here follows that definition

    # for u in list_u:
    #     uids = sample(xrange(1, num_users), int(0.4 * num_users))
    #     users = map(lambda x:list_u[x], uids)
    #     u.send_asset_to_xyz(users)


    while True:
        for u in list_u:
            Timer(60, u.get_cards())

        time.sleep(60)

if __name__ == '__main__':

    main()
