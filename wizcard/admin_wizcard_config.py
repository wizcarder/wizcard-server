__author__ = 'aammundi'

THUMBNAIL_IMAGE_PATH = "test/bizcard.jpeg"
VIDEO_URL = "https://youtu.be/QujpdmsXAb4"
BIZCARD_IMAGE_PATH = "https://s3-us-west-1.amazonaws.com/wizcard-image-bucket-dev/wizcard_admin/bizcard.jpeg"
ADMIN_ASSETS_PATH="assets/admin_wizcard/"
BIZCARD_FILE = "bizcard.jpeg"
THUMBNAIL_FILE = "TN1.jpeg"
#BIZCARD_IMAGE_PATH = ADMIN_ASSETS_PATH+BIZCARD_FILE
#THUMBNAIL_IMAGE_PATH = ADMIN_ASSETS_PATH+THUMBNAIL_FILE

ext_fields = {
    'Facebook': "https://www.facebook.com/getwizcard/#",
    'Twitter': 'https://twitter.com/wizcarder',
    'LinkedIn': 'https://www.linkedin.com/in/wizcard-administrator-2a866696',
    'Web': 'http://www.getwizcard.com',
    'about_me': "I believe when people meet, they should be able to exchange more than just a piece of Dead paper. "
                "They should be able to instantly ANNOUNCE their PERSONA - What I call WizCard...An Alive digital expression of WHO YOU ARE. "
                "I help WizCarders like you Discover, Exchange and Connect with People, Entities, THINGS: around you. "
                "I hope to get better as I evolve. "
                "I also hope you will help spread the Green Word. "
                "Happy WizCarding"
}

w = {
    'first_name': "Wizard Of",
    'last_name': "WizCard",
    'email': "admin@getwizcard.com",
    'phone': "+14084641727",
    'ext_fields': ext_fields
}

wizcard_media = [
      {
        "media_element": VIDEO_URL,
        "media_iframe": "http://www.eventone.com",
        "media_type": "VID",
        "media_sub_type": "ROL"
      },
      {
        "media_element": "http://www.eventone.com",
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

