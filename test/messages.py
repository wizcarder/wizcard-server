
#TODO: Probably should keep the message definition separate and read the
# data into it from a text/db file

from datetime import datetime

LAT1 = 37.885938
LNG1 = -122.506419

NEXMO_PHONE1 = "14084641727"
NEXMO_PHONE2 = "+918971546485"

PHONE1 = "+14084641727"
PHONE2 = "+15085332708"
PHONE3 = "+14086892263"
PHONE4 = "+15086892263"

DELETE_ROLODEX_PHONE1 = "+919986134853"
DELETE_ROLODEX_PHONE2 = "+919845123397"
DELETE_ROLODEX_PHONE3 = "+917259617853"

FUTURE_PHONE1 = "+11111111111"
FUTURE_PHONE2 = "+12222222222"
FUTURE_PHONE3 = "+13333333333"
FUTURE_PHONE4 = "+14444444444"
FUTURE_USERNAME1 = FUTURE_PHONE1+'@wizcard.com'
FUTURE_USERNAME2 = FUTURE_PHONE2+'@wizcard.com'
FUTURE_USERNAME3 = FUTURE_PHONE3+'@wizcard.com'
FUTURE_USERNAME4 = FUTURE_PHONE4+'@wizcard.com'
FUTURE_EMAIL1 = "abcd@future.com"
FUTURE_EMAIL2 = "efgh@future.com"
FUTURE_EMAIL3 = "ijkl@future.com"
FUTURE_EMAIL4 = "mnop@future.com"
OCR_PHONE = "+919590203441"
OCR_USERNAME = OCR_PHONE+'@wizcard.com'


EMAIL1 = "aammundi@gmail.com"
EMAIL2 = "amsaha@gmail.com"
EMAIL3 = "wizcard1@gmail.com"
EMAIL4 = "nothere@gmail.com"

USER1_AB = [
    {
        'name': "Anand Ammundi",
        'phone': PHONE1,
        'email': EMAIL1
    },
    {
        'name': "Andy Ammundi",
        'phone': PHONE1,
        'email': EMAIL1,
    },
    {
        'name': "Anand Ramani",
        'phone': PHONE2,
        'email': EMAIL2
    },
    {
        'name': "Akash Jindal",
        'phone': PHONE3,
        'email': EMAIL3
    },
    {
        'name': "Ishaan Ammundi",
        'phone': PHONE4,
        'email': EMAIL4
    },
    {
        'name': "Sang",
        'phone': FUTURE_PHONE1,
        'email': FUTURE_EMAIL1
    },
]



USER2_AB = [
    {
        'name': "Anand Ammundi",
        'phone': PHONE1,
        'email': EMAIL1
    },
    {
        'name': "Andy Ammundi",
        'phone': PHONE1,
        'email': EMAIL2,
    },
    {
        'name': "Anand Ramani",
        'phone': PHONE2,
        'email': EMAIL2
    },
    {
        'name': "Akash Jindal",
        'phone': PHONE3,
        'email': EMAIL3
    },
    {
        'name': "Ishaan Ammundi",
        'phone': PHONE4,
        'email': EMAIL4
    },
    {
        'name': "Sang",
        'phone': FUTURE_PHONE1,
        'email': FUTURE_EMAIL1
    }
]

phone_check_req = {
    "header" : {
        "msgType" : "phone_check_req",
        "deviceID": "",
        "hash":""
    },
    "sender" : {
        "username" : "",
        "responseMode" : "",
        "target" : "",
        "test_mode": True
    },
}

phone_check_resp = {
    "header" : {
        "msgType" : "phone_check_rsp",
        "deviceID": "",
        "hash":""
    },
    "sender" : {
        "username" : "",
        "responseKey" : ""
    },
}


login = {
    "header" : {
        "msgType" : "login",
        "deviceID": "1234",
        "hash":"xyz123"
    },
    "sender" : {
        "username" : "",
        "userID": "",
        "password": "wizcard"
    },
}

register_sync = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "register",
    },
    "sender" : {
        #maybe should have a separate data file for lat, lng and read with some
        #random index from there
        "lat" : 37.785834,
        "lng" : -122.406415,
        "deviceType": "ios",
        "reg_token": "6c4f3dcb31cb45bdaf399206ea065b9795bee698cd56a60bcd40ee336741d4dd",
        "userID" : "2UIPIEPbBk"

    },
}


register1 = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "register",
    },
    "sender" : {
        #maybe should have a separate data file for lat, lng and read with some
        #random index from there
        "reg_token": "6c4f3dcb31cb45bdaf399206ea065b9795bee698cd56a60bcd40ee336741d4dd",
        "lat" : 37.785835,
        "lng" : -122.406416,
        "deviceType": "ios",
        "userID" : "",
        "wizUserID" : "",
    },
}

register2 = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17C",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "register",
    },
    "sender" : {
        #maybe should have a separate data file for lat, lng and read with some
        #random index from there
        "reg_token": "6c4f3dcb31cb45bdaf399206ea065b9795bee698cd56a60bcd40ee336741d4dd",
        "lat" : 37.785837,
        "lng" : -122.406418,
        "deviceType": "ios",
        "userID" : "",
        "wizUserID" : ""
    },
}

register3 = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17D",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "register",
    },
    "sender" : {
        #maybe should have a separate data file for lat, lng and read with some
        #random index from there
        "reg_token": "6c4f3dcb31cb45bdaf399206ea065b9795bee698cd56a60bcd40ee336741d4dd",
        "lat" : 37.785838,
        "lng" : -122.406419,
        "deviceType": "ios",
        "userID" : "",
        "wizUserID" : ""
    },
}
ocr_register = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17D",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "register",
    },
    "sender" : {
        #maybe should have a separate data file for lat, lng and read with some
        #random index from there
        "reg_token": "6c4f3dcb31cb45bdaf399206ea065b9795bee698cd56a60bcd40ee336741d4dd",
        "lat" : 37.785838,
        "lng" : -122.406419,
        "deviceType": "android",
        "userID" : "",
        "wizUserID" : ""
    },
}

location = {
    "header" : {
        "deviceID" : "",
        "hash" : "",
        #above 2 fields are not currently used by server
        "msgType" : "current_location",
    },
    "sender" : {
        #maybe should have a separate data file for lat, lng and read with some
        #random index from there
        "lat" : "",
        "lng" : "",
        "userID" : "",
        "wizUserID" : ""
    },
}

contacts_verify = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17D",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "contacts_verify",
    },
    "sender" : {
        #maybe should have a separate data file for lat, lng and read with some
        #random index from there
        "userID" : "",
        "wizUserID" : "",
    },
    "receiver" : {
        "verify_phones" : "",
        "verify_emails" : "",
    }

}


contacts_upload = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17D",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "contacts_upload",
    },
    "sender" : {
        #maybe should have a separate data file for lat, lng and read with some
        #random index from there
        "userID" : "",
        "wizUserID" : "",
    },
    "receiver" : {
        "prefix" : "",
        "country_code" : "",
        'ab_list': []
    }

}

contact_container = {
    "company": "Wizcard Inc",
    "title" : "CEO",
    "f_bizCardImage" : "",
    "r_bizCardImage" : "",
    "start" : "xxx",
    "end" : "current",
    "phone": "12345678",
    "card_url": ""
}



edit_card1 = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "edit_card",
    },
    "sender" : {
        #maybe should have a separate data file for lat, lng and read with some
        #random index from there
        "address_city" : "San Francisco Bay Area",
        "address_state" : "CA",
        "address_street1" : "1914 N Marthilda Ave",
        "address_zip" : 94087,
        "email" : "aammundi@gmail.com",
        "first_name" : "Anand",
        "last_name" : "Ammundi",
        "imageWasEdited" : "0",
        "location" : "San Francisco Bay Area",
        "phone1" : PHONE1,
        "userID" : "USER1",
        "deviceType": "ios",
        #wizUserID should be the userID got from response of above register message
        "wizUserID" : "",
        "contact_container" : [contact_container, contact_container, contact_container]
    },
}


edit_card2 = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17C",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "edit_card",
    },
    "sender" : {
        #maybe should have a separate data file for lat, lng and read with some
        #random index from there
        "address_city" : "San Francisco Bay Area",
        "address_state" : "CA",
        "address_street1" : "1914 N Marthilda Ave",
        "address_zip" : 94087,
        "email" : "amsaha@gmail.com",
        "first_name" : "Amit",
        "last_name" : "Saha",
        "imageWasEdited" : "0",
        "location" : "San Francisco Bay Area",
        "phone1" : OCR_PHONE,
        "userID" : "USER2",
        #wizUserID should be the userID got from response of above register message
        "wizUserID" : "",
        "contact_container" : [contact_container, contact_container, contact_container]
    },
}


edit_card3 = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17D",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "edit_card",
    },
    "sender" : {
        #maybe should have a separate data file for lat, lng and read with some
        #random index from there
        "address_city" : "San Francisco Bay Area",
        "address_state" : "CA",
        "address_street1" : "1914 N Marthilda Ave",
        "address_zip" : 94087,
        "email" : "wizard1@gmail.com",
        "first_name" : "Wizard",
        "last_name" : "One",
        "imageWasEdited" : "0",
        "location" : "San Francisco Bay Area",
        "phone1" : PHONE3,
        "userID" : "USER3",
        #wizUserID should be the userID got from response of above register message
        "wizUserID" : "",
        "contact_container" : [contact_container, contact_container, contact_container]
    },
}


table_create = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "create_table",
    },
    "sender" : {
        "lat" : 37.785838,
        "lng" : -122.406419,
        "deviceType": "ios",
        "userID" : "",
        "wizUserID" : "",
        "table_name" : "",
        "timeout": 1,
        "secureTable" : "True",
        "password" : "test",
        "created":str(datetime.now())
    },
}

send_asset_to_xyz= {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "send_asset_to_xyz",
    },
    #senderID can be wizCardID or tableID
    "sender" : {
        #asset type can be wizcard, table, forwarded_wizcard
        "assetID" : "",
        "assetType": ""
    },
    "receiver" : {
        #receiver type can be wiz_untrusted, wiz_trusted, wiz_trusted_check
        #for in-network. email, sms for non-wiz network (future handliing)
        "receiverType" : "",
        #receiver id's can be phone, email, wizUserID
        "receiverIDs" : []
    }
}


send_to_user = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "send_card_to_user",
    },
    "receiver" : {
        "wizUserIDs" : []
    }
}


send_to_contacts = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "send_card_to_contacts",
    },
    "receiver" : {
        "wizUserIDs" : []
    }
}

send_to_future_contacts = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "send_card_to_future_contacts",
    },
    "receiver" : {
        "phones" : []
    }
}

table_join = {
    "header" : {
        "deviceID" : "5AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f02460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "join_table",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
        "tableID": "",
        "password" : "test"
    },
}

table_edit = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "table_edit",
    },
    "sender" : {
        "lat" : 37.785838,
        "lng" : -122.406419,
        "deviceType": "ios",
        "userID" : "",
        "wizUserID" : "",
        "tableID": "",
        "table_name" : "",
        "oldName":"",
        "newName":"",
        "timeout":5,
        "created":str(datetime.now())
    },
}

table_query = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "query_tables",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
    },
    "receiver" : {
        "name": "",
    },
}

table_summary = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "table_summary",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
        "tableID": ""
    }
}

table_details = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "table_details",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
        "tableID": ""
    }
}

card_flick = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "card_flick",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
        "lat" : 37.785834,
        "lng" : -122.406415,
        "timeout": 1,
        "deviceType": "ios",
        "created":str(datetime.now())

    },
}

card_flick_accept = {
    "header" : {
        "deviceID" : "55C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f02460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "card_flick_accept",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
    },
    "receiver" : {
        "flickCardIDs" : "",
    }
}
accept_connection_request = {
    "header" : {
        "deviceID" : "55C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f02460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "accept_connection_request",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
        "reaccept" : False,
        # this is dummy...the right thing to do is to get the
        # correct notif_id from the get_cards and pass it back in here
        "notif_id": 1
    },
    "receiver" : {
        "wizUserID" : "",
    }
}

decline_connection_request = {
    "header" : {
        "deviceID" : "55C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f02460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "decline_connection_request",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
        "notif_id": 1

    },
    "receiver" : {
        "wizCardID" : "",
    }
}

flick_pickers = {
    "header" : {
        "deviceID" : "55C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f02460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "flick_pickers",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
        "flickCardIDs" : "",
    },
}

card_flick_edit = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "flick_edit",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
        "flickCardID": "",
        "timeout":"",
        "created":str(datetime.now())
    },
}

user_query = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "send_query_user",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
    },
    "receiver" : {
        "name": "",
    },
}

card_flick_query = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "query_flicks",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
    },
    "receiver" : {
        "name": "",
    },
}

my_flicks = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "my_flicks",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
        "wizCardID" : ""
    }
}


get_cards = {
    "header" : {
        "deviceID" : "17b90b2e03dc7b38",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "get_cards",
    },
    "sender" : {
        "deviceType": "android",
        "lat": LAT1,
        "lng": LNG1
    },
}

delete_rolodex_card = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "delete_rolodex_card",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : ""
    },
    "receiver" : {
        "wizCardIDs" : ""
    }
}

card_details = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "get_card_details",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
    },
    "receiver" : {
        "wizCardID" : "",
    }
}

ocr_req_self = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "ocr_req_self",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
    },
}

ocr_dead_card = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "ocr_req_dead_card",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
    },
}

ocr_dead_card_edit = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "ocr_dead_card_edit",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
        "deadCardID": "",
        "inviteother" : 0,
        "contact_container": [contact_container]
    },
}
wizweb_query_user = {
    "header" : {
        "deviceID" : "wizweb",
        "hash" : "da0f7402460b85205c85618edf685916",
        "msgType" : "wizweb_query_user",
    },
    "sender" : {
        "email" : "xyz@abc.co.in",
        "username" : ""
    },
}


wizweb_query_wizcard = {
    "header" : {
        "deviceID" : "wizweb",
        "hash" : "da0f7402460b85205c85618edf685916",
        "msgType" : "wizweb_query_wizcard",
    },
    "sender" : {
        "email" : "xyz@abc.co.in",
        "username" : ""
    },
}

wizweb_create_user = {
    "header" : {
        "deviceID" : "wizweb",
        "hash" : "da0f7402460b85205c85618edf685916",
        "msgType" : "wizweb_create_user",
    },
    "sender" : {
        "username" : "",
        "first_name" : "",
        "last_name" : ""
    },
}

wizweb_add_edit_card = {
    "header" : {
        "deviceID" : "wizweb",
        "hash" : "da0f7402460b85205c85618edf685916",
        "msgType" : "wizweb_add_edit_card",
    },
    "sender" : {
        "username" : "",
        "userID" : "",
        "first_name" : "",
        "last_name" : "",
        "phone" : "",
        "title" : "",
        "company" : "",
        "mediaUrl" : "",
        "f_bizCardUrl" : "",
        "contact_container" : [contact_container, contact_container, contact_container]
    },
}

meishi_start = {
    "header" : {
        "msgType" : "meishi_start",
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
    },
    "sender" : {
        "userID" : "",
        "wizCardID" : "",
        "lat" : 37.785834,
        "lng" : -122.406415,
        "deviceType": "ios",
    },
}
meishi_find = {
    "header" : {
        "msgType" : "meishi_find",
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
    },
    "sender" : {
        "userID" : "",
        "wizCardID" : "",
        "mID" : "",
        "deviceType": "ios",
    },
}
get_email_template = {
    "header" : {
        "msgType" : "get_email_template",
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
    },
    "sender" : {
        "userID" : "",
        "wizCardID" : "",
        "mID" : "",
        "deviceType": "ios",
    },
}
rolodex_edit_card1 = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17C",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "edit_card",
    },
    "sender" : {
        #maybe should have a separate data file for lat, lng and read with some
        #random index from there
        "address_city" : "Bangalore",
        "address_state" : "KA",
        "address_street1" : "JP Nagar",
        "address_zip" : 560078,
        "email" : "aanandr@gmail.com",
        "first_name" : "Anand",
        "last_name" : "Ramani",
        "imageWasEdited" : "0",
        "location" : "Bangalore",
        "phone1" : OCR_PHONE,
        "userID" : "USER2",
        #wizUserID should be the userID got from response of above register message
        "wizUserID" : "",
	"contact_container" : [contact_container, contact_container, contact_container]
    },
}
rolodex_edit_card2 = {
    "header" : {
	"deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17D",
	"hash" : "da0f7402460b85205c85618edf685916",
	#above 2 fields are not currently used by server
	"msgType" : "edit_card",
    },
    "sender" : {
	#maybe should have a separate data file for lat, lng and read with some
	#random index from there
	"address_city" : "Chennai",
	"address_state" : "TN",
	"address_street1" : "Poes Garden",
	"address_zip" : 600014,
	"email" : "ranandr@gmail.com",
	"first_name" : "Anand",
	"last_name" : "Sankar",
	"imageWasEdited" : "0",
	"location" : "Bangalore",
	"phone1" : OCR_PHONE,
	"userID" : "USER2",
	#wizUserID should be the userID got from response of above register message
	"wizUserID" : "",
	"contact_container" : [contact_container, contact_container, contact_container]
    },
}


rolodex_edit_card3 = {
    "header" : {
	"deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17D",
	"hash" : "da0f7402460b85205c85618edf685916",
	#above 2 fields are not currently used by server
	"msgType" : "edit_card",
    },
    "sender" : {
	#maybe should have a separate data file for lat, lng and read with some
	#random index from there
	"address_city" : "Chandigarh",
	"address_state" : "PJ",
	"address_street1" : "Mohali",
	"address_zip" : 300014,
	"email" : "akashjindal@gmail.com",
	"first_name" : "Akash",
	"last_name" : "Jindal",
	"imageWasEdited" : "0",
	"location" : "Mohali",
	"phone1" : OCR_PHONE,
	"userID" : "USER2",
	#wizUserID should be the userID got from response of above register message
	"wizUserID" : "",
	"contact_container" : [contact_container, contact_container, contact_container]
    },
}

