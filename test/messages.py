
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
EMAIL5 = "amnothere@gmail.com"


USER1_AB = [
    {
        'name': "Anand Ammundi",
        'phone': [PHONE1],
        'email': [EMAIL1]
    },
    {
        'name': "Andy Ammundi",
        'phone': [PHONE1],
        'email': [EMAIL2],
    },
    {
        'name': "Anand Ramani",
        'phone': [PHONE2, PHONE3],
        'email': [EMAIL3]
    },
    {
        'name': "Akash Jindal",
        'phone': [PHONE3],
        'email': [EMAIL4]
    },
    {
        'name': "Ishaan Ammundi",
        'phone': [PHONE4, PHONE1],
        'email': [EMAIL5]
    },
    {
        'name': "Sang",
        'phone': [FUTURE_PHONE1, FUTURE_EMAIL2],
        'email': [FUTURE_EMAIL1]
    },
]



USER2_AB = [
    {
        'name': "A Ammundi",
        'phone': [PHONE1, PHONE2],
        'email': [EMAIL1]
    },
    {
        'name': "Andy Ammundi",
        'phone': [PHONE2],
        'email': [EMAIL1],
    },
    {
        'name': "Anand Ramani",
        'phone': [PHONE2],
        'email': [EMAIL2]
    },
    {
        'name': "Akash Jindal",
        'phone': [PHONE3],
        'email': [EMAIL3]
    },
    {
        'name': "Ishaan Ammundi",
        'phone': [PHONE4],
        'email': [EMAIL4]
    },
    {
        'name': "Sang",
        'phone': [FUTURE_PHONE1],
        'email': [FUTURE_EMAIL1]
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
        "deviceType": "android",
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
        "deviceType": "android",
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
        "deviceType": "android",
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
        "deviceType": "android",
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
        "deviceType": "android",
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
        "deviceType": "android",
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
        "deviceType": "android",
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
        "deviceType": "android",
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

archived_cards = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "archived_cards",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : "",
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

edit_rolodex_card = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "edit_rolodex_card",
    },
    "sender" : {
        "userID" : "",
        "wizUserID" : ""
    },
    "receiver" : {
        "wizCardID" : "",
        "notes" : "",
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
        "deviceType": "android",
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
        "deviceType": "android",
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
        "deviceType": "android",
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

get_recommendations = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17D",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "get_recommendations",
    },
    "sender" : {
        #maybe should have a separate data file for lat, lng and read with some
        #random index from there
        "userID" : "",
        "wizUserID" : "",
    },
}

# Canned Messages
ab_list_big_1 = {
    u'ab_list':
        [
            {u'phone': [u'+919444005358'], u'contactID': u'599', u'email': [], u'name': u'Achan'}, {u'phone': [], u'contactID': u'524', u'email': [u'adayal01@gmail.com'], u'name': u'Aditya Dayal'}, {u'phone': [], u'contactID': u'191', u'email': [u'ajitmenons@gmail.com'], u'name': u'Ajit Menon'}, {u'phone': [u'9872016191', u'+918699235456', u'7009432094'], u'contactID': u'1672', u'email': [], u'name': u'Akash Jindal'}, {u'phone': [u'+919444065358'], u'contactID': u'593', u'email': [], u'name': u'Amma'}, {u'phone': [u'+919449994226'], u'contactID': u'704', u'email': [], u'name': u'Amma Mysore'}, {u'phone': [u'9094460920'], u'contactID': u'1670', u'email': [], u'name': u'Anand Raj Driver'}, {u'phone': [], u'contactID': u'1627', u'email': [u'anandramani98@gmail.com'], u'name': u'Anand Ramani'}, {u'phone': [u'+918971546485'], u'contactID': u'1700', u'email': [], u'name': u'Anand Ramani'}, {u'phone': [u'+15127045497'], u'contactID': u'591', u'email': [], u'name': u'Anna'}, {u'phone': [], u'contactID': u'539', u'email': [u'annajeenott@gmail.com'], u'name': u'Annajee Nott'}, {u'phone': [], u'contactID': u'533', u'email': [u'subramanian.anu@gmail.com'], u'name': u'Anu Subramanian'}, {u'phone': [], u'contactID': u'528', u'email': [u'anupama.natarajan@gmail.com'], u'name': u'Anupama Natarajan'}, {u'phone': [u'+918606063317'], u'contactID': u'1688', u'email': [], u'name': u'Arun Foofys'}, {u'phone': [u'+919962604386'], u'contactID': u'1666', u'email': [], u'name': u'Avinash Jayakumar'}, {u'phone': [u'+919840740851'], u'contactID': u'1687', u'email': [], u'name': u'Balaji Venkat'}, {u'phone': [], u'contactID': u'541', u'email': [u'mrbaskaran@gmail.com'], u'name': u'Baskaran Rajaraman'}, {u'phone': [u'9841312441'], u'contactID': u'1685', u'email': [], u'name': u'Benjamin Driver'}, {u'phone': [], u'contactID': u'1538', u'email': [u'k_vj_c@yahoo.com'], u'name': u'Chander Vijay'}, {u'phone': [u'+919884079353'], u'contactID': u'1677', u'email': [], u'name': u'Chumar Varghese'}, {u'phone': [u'9791062513'], u'contactID': u'1692', u'email': [], u'name': u'Col Govind Reddy'}, {u'phone': [], u'contactID': u'1342', u'email': [u'a@b.com'], u'name': u'Conf Bridge'}, {u'phone': [u'+6287861645844'], u'contactID': u'702', u'email': [], u'name': u'Dede'}, {u'phone': [], u'contactID': u'540', u'email': [u'deepapoduval@gmail.com'], u'name': u'Deepa Poduval'}, {u'phone': [], u'contactID': u'532', u'email': [u'deepavikram@gmail.com'], u'name': u'Deepa Vikram'}, {u'phone': [], u'contactID': u'552', u'email': [u'maildhananjay@gmail.com'], u'name': u'Dhananjay Chithathoor'}, {u'phone': [], u'contactID': u'566', u'email': [u'dhiren9@gmail.com'], u'name': u'Dhiren Bhatia'}, {u'phone': [u'+919884458888'], u'contactID': u'688', u'email': [], u'name': u'Divya'}, {u'phone': [], u'contactID': u'544', u'email': [u'divya.acharya@gmail.com'], u'name': u'Divya Rajan'}, {u'phone': [u'9364555554'], u'contactID': u'1707', u'email': [], u'name': u'Dr Sundaram Bone'}, {u'phone': [u'+919790977991'], u'contactID': u'1689', u'email': [], u'name': u'Eswar'}, {u'phone': [u'+15125608414'], u'contactID': u'586', u'email': [], u'name': u'Garima'}, {u'phone': [u'+1(408)6607706'], u'contactID': u'1679', u'email': [], u'name': u'Gayathri'}, {u'phone': [], u'contactID': u'543', u'email': [u'gitamuralidharan7@gmail.com'], u'name': u'geetha muralidharan'}, {u'phone': [], u'contactID': u'410', u'email': [u'hello@glamstorm.com'], u'name': u'GLAMSTORM'}, {u'phone': [u'7550088776'], u'contactID': u'1664', u'email': [], u'name': u'Hari Trainer'}, {u'phone': [u'+919841462314'], u'contactID': u'1675', u'email': [], u'name': u'Ishwar Swimming'}, {u'phone': [], u'contactID': u'535', u'email': [u'jayendra.g@gmail.com'], u'name': u'Jayendra Gowrishankar'}, {u'phone': [], u'contactID': u'118', u'email': [u'jyothivinod@gmail.com'], u'name': u'Jo'}, {u'phone': [u'15126621457'], u'contactID': u'672', u'email': [], u'name': u'Johnathan Realtor'}, {u'phone': [], u'contactID': u'145', u'email': [u'jyothisreevalsan@gmail.com'], u'name': u'Jyothi Sreevalsan'}, {u'phone': [u'+15125695878'], u'contactID': u'1691', u'email': [], u'name': u'Karen Kelly'}, {u'phone': [], u'contactID': u'642', u'email': [u'newmumintown@hotmail.com'], u'name': u'Kavitha Menon'}, {u'phone': [], u'contactID': u'526', u'email': [u'newmumintown@gmail.com'], u'name': u'Kavitha Menon, ( Hey New Pics Guys)'}, {u'phone': [], u'contactID': u'346', u'email': [u'kgmuthukumar@gmail.com'], u'name': u'KG Muthukumar'}, {u'phone': [u'+919841049545'], u'contactID': u'581', u'email': [], u'name': u'Kora'}, {u'phone': [u'+919739793537'], u'contactID': u'1671', u'email': [], u'name': u'Kripa V'}, {u'phone': [], u'contactID': u'160', u'email': [u'laksjayaraj@gmail.com'], u'name': u'Lakshmi Sankaranarayanan'}, {u'phone': [u'+919940334395'], u'contactID': u'700', u'email': [], u'name': u'Lalitha Swarup'}, {u'phone': [u'9444005358'], u'contactID': u'1681', u'email': [], u'name': u'Lata Ramachandran'}, {u'phone': [u'+15129481732'], u'contactID': u'1549', u'email': [], u'name': u'Maithri'}, {u'phone': [u'+1(571)4811550'], u'contactID': u'1683', u'email': [], u'name': u'Manju Majhi'}, {u'phone': [u'+15129561156'], u'contactID': u'685', u'email': [], u'name': u'Manya'}, {u'phone': [u'+919094077861'], u'contactID': u'686', u'email': [], u'name': u'Martha'}, {u'phone': [u'9445981973'], u'contactID': u'1669', u'email': [], u'name': u'Mathew Srampickal'}, {u'phone': [u'+919845167896'], u'contactID': u'1661', u'email': [], u'name': u'Mekin Maheshwari'}, {u'phone': [], u'contactID': u'112', u'email': [u'MethilP@ducont.com'], u'name': u'Methil Prasad'}, {u'phone': [u'9841010518'], u'contactID': u'1706', u'email': [], u'name': u'Michael Boat Club'}, {u'phone': [u'9916528153'], u'contactID': u'1548', u'email': [], u'name': u'Murli'}, {u'phone': [u'15185775345'], u'contactID': u'671', u'email': [], u'name': u'Nate'}, {u'phone': [u'+919841022120'], u'contactID': u'1686', u'email': [], u'name': u'Nisha'}, {u'phone': [u'9884061057'], u'contactID': u'1663', u'email': [], u'name': u'Prabhakar'}, {u'phone': [], u'contactID': u'107', u'email': [u'priya.dhananjay@gmail.com'], u'name': u'Priya Dhananjay'}, {u'phone': [], u'contactID': u'536', u'email': [u'priya.kesavan@gmail.com'], u'name': u'Priya Kesavan'}, {u'phone': [], u'contactID': u'531', u'email': [u'pvattyam@yahoo.com'], u'name': u'Priya Vattyam'}, {u'phone': [u'9840023975'], u'contactID': u'1659', u'email': [], u'name': u'Rajaram S'}, {u'phone': [u'+919840015160'], u'contactID': u'1676', u'email': [], u'name': u'Rajeevettan'}, {u'phone': [], u'contactID': u'555', u'email': [u'rivendell@rivendellgreaterswiss.com'], u'name': u'Rivendell'}, {u'phone': [u'+1(408)8359989'], u'contactID': u'1662', u'email': [], u'name': u'Rudra'}, {u'phone': [], u'contactID': u'646', u'email': [u'rudrarugge@gmail.com'], u'name': u'Rudra Rugge'}, {u'phone': [u'+447887744780'], u'contactID': u'597', u'email': [], u'name': u'Sabi'}, {u'phone': [u'\u202a+919176049984\u202c'], u'contactID': u'663', u'email': [], u'name': u'Sangita Ramachandran'}, {u'phone': [], u'contactID': u'359', u'email': [u'sanjumenon@gmail.com'], u'name': u'sanjay menon'}, {u'phone':
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         [u'+919003034900'], u'contactID': u'1667', u'email': [], u'name': u'Shahid Kerala Contact'}, {u'phone': [u'9367422334', u'9363212334'], u'contactID': u'1678', u'email': [], u'name': u'Shankar'}, {u'phone': [u'9840631114'], u'contactID': u'1665', u'email': [], u'name': u'Siddhart Nisha'}, {u'phone': [], u'contactID': u'621', u'email': [u'sindujas@gmail.com'], u'name': u'Sinduja Subramanian'}, {u'phone': [u'+15123487833'], u'contactID': u'665', u'email': [], u'name': u'Sit Means Sit Carrie'}, {u'phone': [], u'contactID': u'607', u'email': [u'sruti_soman@yahoo.co.uk'], u'name': u'Sruti Ayinikatt'}, {u'phone': [u'+447502346614'], u'contactID': u'598', u'email': [], u'name': u'Suji'}, {u'phone': [], u'contactID': u'549', u'email': [u'sumitramani@hotmail.com'], u'name': u'Sumitra Mani'}, {u'phone': [], u'contactID': u'529', u'email': [u'tanyas@gmail.com'], u'name': u'Tanya Shastri'}, {u'phone': [u'(310)8869070'], u'contactID': u'674', u'email': [], u'name': u'Tatyana'}, {u'phone': [], u'contactID': u'537', u'email': [u'uday.keshavdas@gmail.com'], u'name': u'Uday Keshavdas'}, {u'phone': [u'+919538345536'], u'contactID': u'1674', u'email': [], u'name': u'Uma Chitti'}, {u'phone': [], u'contactID': u'564', u'email': [u'bharvani@mba.berkeley.edu', u'vbharvani@gmail.com'], u'name': u'Vandana Bharvani'}, {u'phone': [u'9253211669', u'9254152425'], u'contactID': u'1095', u'email': [], u'name': u'Vijay C'}, {u'phone': [u'9741252423'], u'contactID': u'1660', u'email': [u'vikram@foofys.com'], u'name': u'Vikram Foofys'}, {u'phone': [], u'contactID': u'538', u'email': [u'vikramesh@gmail.com'], u'name': u'Vikram Ramesh'}, {u'phone': [u'+919900480665'], u'contactID': u'1559', u'email': [u'vikram.srinivasan@gmail.com'], u'name': u'Vikram Srinivasan'}, {u'phone': [u'+15125500529'], u'contactID': u'583', u'email': [], u'name': u'Ximena'}
        ],
    u'country_code': u'+1'
}

