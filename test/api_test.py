from __future__ import division

import random
import messages
import libtest
from libtest import send_request, handle_response
import httplib
import names
import pdb

SERVER_URL = 'localhost'
SERVER_PORT = 8000


# should move to singleton class
global_user_list = []

import string
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


class Connect(object):
    def __init__(self, server_url=SERVER_URL, server_port=SERVER_PORT, *kwargs):
        self.server_url = server_url
        self.server_port = server_port
        self.conn = httplib.HTTPConnection(SERVER_URL, SERVER_PORT)
        self.device_id = "DUMMY_DEVICE_ID"
        self.msg_hdr = dict(header=dict(device_id=self.device_id, hash='DUMMY', version=messages.APP_VERSION))
        self.reqmsg = {}

    def send(self):
        self.reqmsg['header'].update(self.msg_hdr['header'])
        send_request(self.conn, self.reqmsg)
        objs = handle_response(self.conn, self.reqmsg['header']['msg_type'])
        return objs



class User(Connect):
    def __init__(self):
        super(User, self).__init__()

        self.first_name = id_generator()
        self.last_name = id_generator()
        self.username = id_generator()
        self.target = id_generator()
        self.response_mode = 'sms'
        self.global_index = len(global_user_list)

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
        self.reqmsg['sender']['first_name'] = names.get_first_name()
        self.reqmsg['sender']['last_name'] = names.get_last_name()
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


    def entity_join(self, entity_id, entity_type='EVT'):
        self.reqmsg = messages.entity_join.copy()
        self.reqmsg['header'].update(self.msg_hdr['header'])

        self.reqmsg['sender']['user_id'] = self.uid
        self.reqmsg['sender']['wizuser_id'] = self.wuid
        self.reqmsg['sender']['entity_id'] = entity_id
        self.reqmsg['sender']['entity_type'] = entity_type

        send_request(self.conn, self.reqmsg)
        objs = handle_response(self.conn, self.reqmsg['header']['msg_type'])




class Poll(Connect):

    TRUE_FALSE_CHOICE = 'TOF'
    SCALE_OF_1_X_CHOICE = 'SCL'
    MULTIPLE_CHOICE = 'MCR'
    QUESTION_ANSWER_TEXT = 'TXT'

    def __init__(self, *args, **kwargs):
        super(Poll, self).__init__()
        self.data = kwargs
        self.reqmsg = messages.poll_response.copy()
        self.reqmsg['sender']['user_id'] = args[0]
        self.reqmsg['sender']['wizuser_id'] = args[1]
        self.reqmsg['sender']['entity_id'] = self.data['id']

    def prepare_response(self):
        for q in self.data['questions']:
            question_type = q['question_type']
            choices = q['choices']
            if question_type == self.TRUE_FALSE_CHOICE:
                self.true_false_response(q['id'], choices)
            elif question_type == self.SCALE_OF_1_X_CHOICE:
                self.one_to_x_response(q['id'], choices)
            elif question_type == self.MULTIPLE_CHOICE:
                self.mct_response(q['id'], choices)
            elif question_type == self.QUESTION_ANSWER_TEXT:
                self.text_response(q['id'], choices)

    def true_false_response(self, qid, choices):
        response = messages.poll_questions_response.copy()
        response['question_id'] = qid
        response['answer_id'] = choices[0]['id']
        response['has_boolean_value'] = True
        response['boolean_value'] = random.choice([True, False])
        self.reqmsg['sender']['responses'].append(response)

    def one_to_x_response(self, qid, choices):
        response = messages.poll_questions_response.copy()
        response['question_id'] = qid
        response['answer_id'] = choices[0]['id']
        response['has_user_value'] = True
        response['user_value'] = random.choice(range(1, 6))
        self.reqmsg['sender']['responses'].append(response)

    def mct_response(self, qid, choices):
        response = messages.poll_questions_response.copy()
        response['question_id'] = qid
        response['answer_id'] = choices[random.choice(range(1, len(choices)+1))]['id']
        self.reqmsg['sender']['responses'].append(response)

    def text_response(self, qid, choices):
        response = messages.poll_questions_response.copy()
        response['question_id'] = qid
        response['has_text'] = True
        response['text'] = 'Some random text'
        self.reqmsg['sender']['responses'].append(response)


