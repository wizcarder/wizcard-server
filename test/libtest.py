__author__ = 'aammundi'

import pprint
import json
import pdb
from wizcard import settings

ocr_image_path = "test/1-f_bc.2.2015-06-21_2056.jpg"
#test_image_path = "test/photo.JPG"
#ocr_image_path = "test/1-f_bc.2.2015-06-21_2056.jpg"
test_image_path = "test/1-f_bc.2.2015-06-21_2056.jpg"



APP_VERSION = str(settings.APP_MAJOR) + "." +  str(settings.APP_MINOR)


def send_request(conn, req):
    print("Sending ", req['header']['msg_type'])
    if not req['header']['msg_type'] in ['ocr_req_self', 'ocr_req_dead_card']:
        pprint.pprint(req)
    jreq = json.dumps(req)
    conn.request("POST", "", jreq)


def handle_response(conn, msg_type, err_skip=False):
    res = conn.getresponse()
    print res.status, res.reason
    objs = res.read()
    objs = json.loads(objs)
    print "received respone for Message: ", msg_type
    print json.dumps(objs, sort_keys = True, indent = 2)

    if objs['result']['Error']:
        print "Error Response: ", objs['result']
        if not err_skip:
            exit()

    return objs


def check_obj_for_key(obj, key):
    res = obj['data']['result']
    if key in res:
        return res[key]

    return None

