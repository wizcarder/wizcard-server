
#!/usr/bin/python

# Test WizCard client (the real one resides on a smartphone - iphone, android)

register1 = {
    "deviceID": "A000111",
    "userID": "aammundi",
    "firstname":"Anand",
    "lastname":"Ammundi",
    "seqNum": "1000",
    "msgType":"register",
    "message": {"lat":37.32300, "lng":-122.03218}
}

register2 = {
    "deviceID": "A000113",
    "userID": "ishaan",
    "firstname":"Ishaan",
    "lastname":"Ammundi",
    "seqNum": "1000",
    "msgType":"register",
    "message": {"lat":37.32300, "lng":-122.03218}
}

register3 = {
    "deviceID": "A000112",
    "userID": "ronak",
    "firstname":"Ronak",
    "lastname":"Shah",
    "seqNum": "1000",
    "msgType":"register",
    "message": {"lat":37.32300, "lng":-122.03218}
}

register4 = {
    "deviceID": "A000112",
    "userID": "mariya",
    "firstname":"Mariya",
    "lastname":"Kholod",
    "seqNum": "1000",
    "msgType":"register",
    "message": {"lat":37.32300, "lng":-122.03218}
}

register5 = {
    "deviceID": "A000112",
    "userID": "rudra",
    "firstname":"Rudra",
    "lastname":"Rugge",
    "seqNum": "1000",
    "msgType":"register",
    "message": {"lat":37.32300, "lng":-122.03218}
}

register6 = {
    "deviceID": "A000112",
    "userID": "pranay",
    "firstname":"Pranay",
    "lastname":"Pogde",
    "seqNum": "1000",
    "msgType":"register",
    "message": {"lat":37.32300, "lng":-122.03218}
}

add_card1 = {
    "deviceID" : "A00195EE-2A42-4E2F-9EFF-8FBD3475164B",
    "message": {
        "city" : "CityName",
        "company" : "1",
        "email" : "1@test.com",
        "first" : "Anand",
        "last" : "Ammundi",
        "phone" : "123456789",
        "state" : "StateName",
        "street" : "StreetName",
        "thumbnailImage" : "...",
        "title" : "My position",
        "zip" : "00000",
    },
    "msgType" : "add_card",
    "seqNum" : "1000",
    "userID" : "aammundi",
}

add_card2 = {
    "deviceID" : "A00195EE-2A42-4E2F-9EFF-8FBD3475164B",
    "message": {
        "city" : "CityName",
        "company" : "2",
        "email" : "2@test.com",
        "first" : "Ishaan",
        "last" : "Ammundi",
        "phone" : "123456789",
        "state" : "StateName",
        "street" : "StreetName",
        "thumbnailImage" : "...",
        "title" : "My position",
        "zip" : "00000",
    },
    "msgType" : "add_card",
    "seqNum" : "1000",
    "userID" : "ishaan"
}

add_card3 = {
    "deviceID" : "A00195EE-2A42-4E2F-9EFF-8FBD3475164B",
    "message": {
        "city" : "CityName",
        "company" : "3",
        "email" : "3@test.com",
        "first" : "Ronak",
        "last" : "Shah",
        "phone" : "123456789",
        "state" : "StateName",
        "street" : "StreetName",
        "thumbnailImage" : "...",
        "title" : "My position",
        "zip" : "00000",
    },
    "msgType" : "add_card",
    "seqNum" : "1000",
    "userID" : "ronak"
}

add_card4 = {
    "deviceID" : "A00195EE-2A42-4E2F-9EFF-8FBD3475164B",
    "message": {
        "city" : "CityName",
        "company" : "4",
        "email" : "4@test.com",
        "first" : "Mariya",
        "last" : "Kholod",
        "phone" : "123456789",
        "state" : "StateName",
        "street" : "StreetName",
        "thumbnailImage" : "...",
        "title" : "My position",
        "zip" : "00000",
    },
    "msgType" : "add_card",
    "seqNum" : "1000",
    "userID" : "mariya"
}

add_card5 = {
    "deviceID" : "A00195EE-2A42-4E2F-9EFF-8FBD3475164B",
    "message": {
        "city" : "CityName",
        "company" : "4",
        "email" : "4@test.com",
        "first" : "Rudra",
        "last" : "Rugge",
        "phone" : "123456789",
        "state" : "StateName",
        "street" : "StreetName",
        "thumbnailImage" : "...",
        "title" : "My position",
        "zip" : "00000",
    },
    "msgType" : "add_card",
    "seqNum" : "1000",
    "userID" : "rudra"
}

add_card6 = {
    "deviceID" : "A00195EE-2A42-4E2F-9EFF-8FBD3475164B",
    "message": {
        "city" : "CityName",
        "company" : "6",
        "email" : "6@test.com",
        "first" : "Pranay",
        "last" : "Pogde",
        "phone" : "123456789",
        "state" : "StateName",
        "street" : "StreetName",
        "thumbnailImage" : "...",
        "title" : "My position",
        "zip" : "00000",
    },
    "msgType" : "add_card",
    "seqNum" : "1000",
    "userID" : "pranay"
}



get_cards1 = {
    "deviceID" : "AOOOOO",
    "userID":       "aammundi",
    "seqNum":       "1000",
    "msgType":      "get_cards"
}

get_cards2 = {
    "deviceID": "A00000",
    "userID":       "ishaan",
    "seqNum":       "1000",
    "msgType":      "get_cards"
}

get_cards3 = {
    "deviceID" : "AP00",
    "userID":       "ronak",
    "seqNum":       "1000",
    "msgType":      "get_cards"
}

get_cards4 = {
    "deviceID" : "AOOOOO",
    "userID":       "mariya",
    "seqNum":       "1000",
    "msgType":      "get_cards"
}

get_cards5 = {
    "deviceID": "A00000",
    "userID":       "rudra",
    "seqNum":       "1000",
    "msgType":      "get_cards"
}

get_cards6 = {
    "deviceID" : "AP00",
    "userID":       "pranay",
    "seqNum":       "1000",
    "msgType":      "get_cards"
}


send_card_to_contacts_1 = {
    "deviceID" : "A090900",
    "message": {
        "wizCardID" : 1,
        "contacts" : [
            {
                "firstName" : "Ishaan",
                "lastName" : "Ammundi"
            },
            {
                "firstName" : "Ronak",
                "lastName" : "Shah"
            }
        ],
    },
    "msgType": "send_card_to_contacts",
    "seqNum": "1000",
    "userID": "aammundi"
}

send_card_to_contacts_2 = {
    "deviceID" : "A090900",
    "message": {
        "wizCardID" : 2,
        "contacts" : [
            {
                "firstName" : "Anand",
                "lastName" : "Ammundi"
            },
            {
                "firstName" : "Ronak",
                "lastName" : "Shah"
            }
        ],
    },
    "msgType": "send_card_to_contacts",
    "seqNum": "1000",
    "userID": "ishaan"
}


send_card_to_contacts_3 = {
    "deviceID" : "A090900",
    "message": {
        "wizCardID" : 3,
        "contacts" : [
            {
                "firstName" : "Anand",
                "lastName" : "Ammundi"
            },
            {
                "firstName" : "Ishaan",
                "lastName" : "Ammundi"
            }
        ],
    },
    "msgType": "send_card_to_contacts",
    "seqNum": "1000",
    "userID": "ronak"
}


send_query_user_4_5 = {
    "deviceID" : "A090900",
    "message": {
        "wizCardID" : 4,
        "user_name" : "rudra",
        "email":"rudra@oz.com",
        "phone":"408-434-1727"
    },
    "msgType": "send_query_user",
    "seqNum": "1000",
    "userID": "mariya"
}

send_query_user_4_6 = {
    "deviceID" : "A090900",
    "message": {
        "wizCardID" : 4,
        "user_name" : "pranay",
        "email":"pranay@oz.com",
        "phone":"408-434-1727"
    },
    "msgType": "send_query_user",
    "seqNum": "1000",
    "userID": "mariya"
}

send_query_user_5_6 = {
    "deviceID" : "A090900",
    "message": {
        "wizCardID" : 5,
        "user_name" : "pranay",
        "email":"pranay@oz.com",
        "phone":"408-444-1727"
    },
    "msgType": "send_query_user",
    "seqNum": "1000",
    "userID": "rudra"
}

send_card_to_user_4_5 = {
    "deviceID" : "A090900",
    "message": {
        "wizCardID" : 4,
        "user_name" : "rudra",
    },
    "msgType": "send_card_to_user",
    "seqNum": "1000",
    "userID": "mariya"
}

send_card_to_user_4_6 = {
    "deviceID" : "A090900",
    "message": {
        "wizCardID" : 4,
        "user_name" : "pranay",
    },
    "msgType": "send_card_to_user",
    "seqNum": "1000",
    "userID": "mariya"
}

send_card_to_user_5_6 = {
    "deviceID" : "A090900",
    "message": {
        "wizCardID" : 5,
        "user_name" : "pranay",
    },
    "msgType": "send_card_to_user",
    "seqNum": "1000",
    "userID": "rudra"
}
