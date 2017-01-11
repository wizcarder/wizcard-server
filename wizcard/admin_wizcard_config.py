__author__ = 'aammundi'

THUMBNAIL_IMAGE_PATH = "test/bizcard.jpeg"
VIDEO_URL = "https://youtu.be/QujpdmsXAb4"
#BIZCARD_IMAGE_PATH = "https://s3-us-west-1.amazonaws.com/wizcard-image-bucket-dev/wizcard_admin/bizcard.jpeg"
ADMIN_ASSETS_PATH="assets/admin_wizcard/"
BIZCARD_FILE = "bizcard.jpeg"
THUMBNAIL_FILE = "TN1.jpeg"
BIZCARD_IMAGE_PATH = ADMIN_ASSETS_PATH+BIZCARD_FILE
THUMBNAIL_IMAGE_PATH = ADMIN_ASSETS_PATH+THUMBNAIL_FILE

ext_fields = {
    'Facebook': "https://www.facebook.com/getwizcard/#",
    'Twitter': 'https://twitter.com/wizcarder',
    'LinkedIn': 'https://www.linkedin.com/in/wizcard-administrator-2a866696',
    'Web': 'http://www.getwizcard.com',
    'about_me': "Hi. I need more material"
}

w = {
    'first_name': "Wizard Of",
    'last_name': "WizCard",
    'email': "admin@getwizcard.com",
    'phone': "+14084641727",
    'videoUrl': VIDEO_URL,
    'extFields': ext_fields
}

cc = {
    'company': "WizCard Inc",
    'title': "Personal Magician",
}

