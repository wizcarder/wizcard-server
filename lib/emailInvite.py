import sys
import StringIO, hashlib
from PIL import Image, ImageFont, ImageDraw
from celery import shared_task
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage as storage


@shared_task
def create_template(wizcard):

    resource = storage.open("/invites/email_template.png")

    data = {"name" : wizcard.first_name + " " + wizcard.last_name, "company": wizcard.get_latest_company(), "title" : wizcard.get_latest_title(), "email" : wizcard.email, "phone" : wizcard.phone}

    position = {'email': '400,440', 'title': '382,400', 'phone': '194,440', 'name':'382,307', 'company' : '382, 373'}
    im = Image.open(resource)
    im_sz = im.size
    im_bg = Image.new(mode='RGBA', size=im_sz, color=(255, 255, 255, 230))
    im_bg.paste(im, (0, 0), 0)

    defaultfont = ImageFont.truetype('arial.ttf', 15)

    try:
        namefont = ImageFont.truetype('Arial Bold.ttf', 20)
    except:
        namefont = ImageFont.truetype('Arial_Bold.ttf', 20)


    draw = ImageDraw.Draw(im_bg)

    for field in position.keys():
        if field == "name":
            font = namefont
        else:
            font = defaultfont


        if data[field]:
            draw.text(map(int, str(position[field]).split(',')), str(data[field]), font=font, fill=(0, 0, 0))

    im_io = StringIO.StringIO()
    im_bg.save(im_io, im.format)
    im_bg.close()
    im.close()
    im_io.seek(0)

    sharefile = SimpleUploadedFile("%s-%s.jpg" % \
                                        (wizcard.pk, now().strftime("%Y-%m-%d %H:%M")),
                                        im_io.getvalue(), "image/jpeg")
    wizcard.emailTemplate.save(sharefile.name, sharefile)
'''

data = {'email': 'anandramani98@gmail.com', 'company':'Yahoo', 'phone':'8971546485', 'title': 'Director Engg', 'name': 'Anand Ramani'}
position = {'email': '100,150', 'title': '100,200', 'phone': '100,250', 'name':'100,100'}
imgstream = create_template(sys.argv[1], data, position)
f = open("bcard.png","w")
f.write(imgstream.getvalue())
f.close
'''
