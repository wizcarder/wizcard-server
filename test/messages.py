
#TODO: Probably should keep the message definition separate and read the 
# data into it from a text/db file
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
        "userID" : "USER1"
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
        "userID" : "USER2"
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
        "userID" : "USER3"
    },
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
        #wizUserID should be the userID got from response of above register message
        "wizUserID" : "",
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
        "userID" : "USER3",
        "wizUserID" : "",
        "lat" : 37.785834,
        "lng" : -122.406415,
    },
}


get_cards_u3 = {
    "header" : {
        "deviceID" : "555C95AE-AEBD-4A9E-9AEA-7A17727BC17B",
        "hash" : "da0f7402460b85205c85618edf685916",
        #above 2 fields are not currently used by server
        "msgType" : "get_cards",
    },
    "sender" : {
        "lat" : 37.785838,
        "lng" : -122.406419,
        "userID" : "",
        "wizUserID" : ""
    },
}


