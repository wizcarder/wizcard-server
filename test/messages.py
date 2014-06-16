
#TODO: Probably should keep the message definition separate and read the 
# data into it from a text/db file

from datetime import datetime


phone_check_req = {
    "header" : {
        "msgType" : "phone_check_req",
        "deviceID": "",
        "hash":""
    },
    "sender" : {
        "username" : "",
        "responseMode" : "",
        "target" : ""
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
        "lat" : 37.785835,
        "lng" : -122.406416,
        "deviceType": "ios",
        "userID" : "",
	"wizUserID" : ""
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
        "lat" : 37.785838,
        "lng" : -122.406419,
        "deviceType": "ios",
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
	"verify_list" : ""
    }
    
}

contact_container = {
    "company": "Wizcard Inc",
    "title" : "CEO",
    "f_bizCardImage" : "",
    "r_bizCardImage" : ""
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
        "phone1" : 4084641727,
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
        "phone1" : 4084642727,
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
        "phone1" : 4084643737,
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
        "secureTable" : "True",
        "password" : "test",
        "created":str(datetime.now())
    },
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
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "get_cards",
    },
    "sender" : {
        "lat" : 37.785838,
        "lng" : -122.406419,
        "deviceType": "ios",
        "userID" : "",
        "wizUserID" : ""
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
        "wizUserID" : ""
    },
    "receiver" : {
        "wizCardID" : ""
    }
}
    

