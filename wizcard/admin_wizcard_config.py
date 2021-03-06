__author__ = 'aammundi'
import os

RUNENV = os.getenv('WIZRUNENV','dev')

# TODO make cleaner...paths have to be based on env settings. Also, access url should be seaparate
# from file path

THUMBNAIL_IMAGE_PATH = "https://s3.ap-south-1.amazonaws.com/wizcard-in-dev/admin/TN1.jpeg"
VIDEO_URL = "https://youtu.be/QujpdmsXAb4"
BIZCARD_IMAGE_PATH = "https://s3-us-west-1.amazonaws.com/wizcard-image-bucket-dev/wizcard_admin/bizcard.jpeg"


ext_fields = {
    'facebook': "https://www.facebook.com/getwizcard/#",
    'twitter': 'https://twitter.com/wizcarder',
    'linkedin': 'https://www.linkedin.com/in/wizcard-administrator-2a866696',
    'web': 'http://www.getwizcard.com',
    'about_me': "Hello. I am the Wizard of WizCard. I'm your personal Event guide. I help put any event in your pocket"
                 "I come packed with loads of helpful tools for you to get the MOST OUT OF ANY EVENT "
                "I also help WizCarders like you Discover, Exchange and Connect with People, Entities, THINGS: around you. "
                "BTW, you can use me in place of your Instant Business Card as well. All your contacts will be safely and"
                "securely stored in your Rolodex. "
                "I hope to get better as I evolve. I also hope you will help spread the Green Word. "
                "Happy WizCarding"
}

w = {
    'email': "admin@getwizcard.com",
    'phone': "+14084641727",
    'ext_fields': ext_fields
}

u = {
    'first_name': "Wizard Of",
    'last_name': "WizCard",
}

wizcard_media = [
      {
        "media_element": VIDEO_URL,
        "media_iframe": "http://www.eventone.com",
        "media_type": "VID",
        "media_sub_type": "ROL"
      },
      {
        "media_element": THUMBNAIL_IMAGE_PATH,
        "media_iframe": "",
        "media_type": "IMG",
        "media_sub_type": "THB"
      },
]

cc_media = [
      {
        "media_element": BIZCARD_IMAGE_PATH,
        "media_iframe": "",
        "media_type": "IMG",
        "media_sub_type": "FBZ"
      },
]

cc = {
    'company': "WizCard Inc",
    'title': "Personal Magician",
}

