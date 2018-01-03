import requests
import sys
import simplejson as json
import event_config as cfg
from random import randint, sample
from datetime import datetime, timedelta
from copy import deepcopy
from api_test import User
import messages
import re
import pdb



headers = {"Content-type": "application/json"}
speaker_ids = []
sponsor_ids = []
campaign_ids = []
agenda_ids = []
event_ids = []
poll_ids = []
taganomy_ids = []
exb_ids = []
filemap = {'speaker':'ceos.tsv', 'sponsor': 'companies.tsv', 'campaign':'companies.tsv'}
#User Login
user_login_payload = {"username": "kappu.biz", "password": "a1b2c3d4"}
user_register_payload = {"username": "", "password1": "a1b2c3d4", "password2": "a1b2c3d4", "email": "", "first_name":"AA", "last_name":"BB", "user_type": 2}

media_payload = {"media_element": "", "media_type": "", "media_sub_type": ""}
speaker_payload = {"name":"", "designation":"", "company":"","ext_fields":{}, "email":"a@b.com", "related":[]}
sponsor_payload = {"name":"", "caption":"", "website": "http://getwizcard.com", "ext_fields":{"linkedin": "http://www.linkedin.com", "twitter": "http://www.twitter.com"}, "phone": "+180090010001", "email":"a@b.com", "description": "Campaign description is here", "address":"1234, Some Lane, Some City, Some Country"}
agenda_payload = {"items":[]}
event_payload = {"name":"", "description":"", "venue": "Pragati Maidan", "location":{'lat':"", 'lng':""}, "start":"", "end":"", "related":[], "website":"http://www.getwizcard.com", "email":"a@b.com"}
event_related_payload = {"related": []}
tag_payload = {"category": "", "tags": {}}
exhibitor_credentials = []
#server = "http://test.wizcard.be:8080/"
server = "http://localhost:8000"

def post_retrieve(rest_path, payload, headers=headers, key="id"):

    request_url = server + rest_path
    resp = requests.post(request_url, json=payload, headers=headers, timeout=10)
    resp_dict = resp.json()
    return resp_dict[key]

def get_retrieve(rest_path, rkey):
    request_url = server + rest_path
    resp = requests.get(request_url, headers=headers, timeout=10)
    resp_dict = resp.json()
    return resp_dict[rkey]

def put_retrieve(rest_path, payload, rkey):
    request_url = server + rest_path
    resp = requests.put(request_url, json=payload, headers=headers, timeout=10)
    resp_dict = resp.json()
    return resp_dict[rkey]


def create_media(url, media_type='IMG', media_sub_type='ROL'):
    media_payload['media_element'] = url
    media_payload['media_type'] = media_type
    media_payload['media_sub_type'] = media_sub_type
    media_id = post_retrieve("/entity/media/", media_payload, key="id")
    return media_id


def create_speakers(num, file):
    f = open(file, "r")
    lines = f.readlines()
    count = len(lines)
    for i in range(0, num):
        rint = randint(0, count-1)
        rline = lines[rint].rstrip()
        (name, designation, company, murl, desc) = rline.split("\t")
        media_id = create_media(murl, media_type='IMG', media_sub_type='THB')
        speaker_payload['name'] = name
        speaker_payload['designation'] = designation
        speaker_payload['company'] = company
        speaker_payload['description'] = desc
        speaker_payload['related'] = [{'ids': [media_id], "type": "e_media"}]
        speaker_id = post_retrieve("/entity/speakers/", speaker_payload, key="id")
        speaker_ids.append(speaker_id)


def create_sponsors(num, file, type="sponsor", attach=False):
    f = open(file, "r")
    lines = f.readlines()
    count = len(lines)
    media_ids = []
    for i in range(0, num):
        rint = randint(0, count-1)
        rline = lines[rint].rstrip()
        (name,  murl, caption) = rline.split("\t")
        media_ids.append(create_media(murl, media_type='IMG', media_sub_type='LGO'))
        num_media = cfg.create_config['campaign_media']
        for i in range(0, num_media):
            media_ids.append(create_media(murl, media_type='IMG', media_sub_type='ROL'))
        sponsor_payload['name'] = name
        sponsor_payload['caption'] = caption[:50]
        sponsor_payload['related'] = [{'ids': media_ids, "type": "e_media"}]
        rest_path = "/entity/%ss/" % type
        sponsor_id = post_retrieve(rest_path, sponsor_payload, key="id")
        if type == 'campaign':
            campaign_ids.append(sponsor_id)
        else:
            sponsor_ids.append(sponsor_id)

        if attach:
            type = "e_" + type
            event_related_payload["related"] = [{"ids": [sponsor_id], "type": type}]
            event_id = event_ids[i]
            rest_path = "/entity/events/" + str(event_id) + "/"
            event_id = put_retrieve(rest_path, event_related_payload, "id")

            tag_id = get_retrieve(rest_path, 'taganomy')
            if tag_id:
                for tid in tag_id:
                    rest_path = "/entity/tags/" + str(tid) + "/"
                    tags = get_retrieve(rest_path, 'tags')
                    random_tags = sample(xrange(1, len(tags)), randint(1, len(tags)))
                    rest_path = "/entity/campaigns/" + str(sponsor_id) + "/"
                    taglist = [tags[x] for x in random_tags]
                    payload = {'tags': taglist, 'taganomy':tid}
                    campaign_id = put_retrieve(rest_path, payload, "id")


def create_events(numevents):
    names = cfg.random_event_names
    edates = cfg.random_dates
    eloc = cfg.random_locations
    rbanners = cfg.random_banners
    event_media = []
    for i in range(0, numevents):
        rint = randint(0,len(names)-1)
        event_payload['name'] = names[rint]
        event_payload['description'] = names[rint] + ". " + names[rint]

        rint = randint(0, len(edates) -1)
        event_payload['start'] = datetime.strptime(edates[rint],"%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(edates[rint], "%Y-%m-%d") + timedelta(days=cfg.create_config['event_interval'])
        end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
        event_payload['end'] = end_date

        rint = randint(0, len(eloc) - 1)
        event_payload['location']['lat'] = eloc[rint]['lat']
        event_payload['location']['lng'] = eloc[rint]['lng']
        event_payload['venue'] = eloc[rint]['venue']

        rand_ids = sample(xrange(1, len(cfg.random_banners)), 3)
        event_media = [create_media(cfg.random_banners[x], media_type='IMG', media_sub_type='BNR') for x in rand_ids]

        rand_ids = sample(xrange(1, len(cfg.random_videos)), int(cfg.create_config['event_media']/2))
        event_media = event_media + [create_media(cfg.random_videos[x], media_type='VID') for x in rand_ids]

        rand_ids = sample(xrange(1, len(cfg.random_images)),
                          int(cfg.create_config['event_media'] - cfg.create_config['event_media']/2))
        event_media = event_media + [create_media(cfg.random_images[x]) for x in rand_ids]

        related_speakers = {"ids": speaker_ids, "type": "e_speaker"}
        related_sponsors = {"ids": sponsor_ids, "type": "e_sponsor"}
        related_campaigns = {"ids": campaign_ids, "type": "e_campaign"}
        related_media = {"ids": event_media, "type": "e_media"}
        related_polls = {"ids": poll_ids, "type": "e_poll"}
        event_payload['related'] = [related_speakers, related_sponsors, related_campaigns, related_media, related_polls]

        event_id = post_retrieve("/entity/events/", event_payload, key="id")
        event_ids.append(event_id)

def create_agenda(numitems, evt, start_date, end_date, speakers ):

    start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
    start_date = start_date + " 09:00:00"
    payload = dict()
    for item in range(0, numitems):
        payload['start'] = start_date
        end_date =  datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)
        end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
        payload["end"] = end_date
        start_date = end_date
        rint = randint(0, len(cfg.random_event_names) - 1)
        payload['name'] = "Talk on %s" % cfg.random_event_names[rint]
        payload['where'] = "Conference Hall %s" % str(item)
        payload['description'] = payload['name'] + " at " + payload['where']
        rint = randint(0, len(speakers) - 1)
        payload['related'] = [{"ids": [speakers[rint]], "type":"e_speaker"}]
        agenda_payload["items"].append(payload)
        payload = {}


        rest_path = "/entity/events/%d/agenda/" % evt
        agenda_id = post_retrieve(rest_path, agenda_payload, key="id")

        agenda_ids.append(agenda_id)

def create_polls():
    for poll_type in cfg.create_config['polls']:
        for i in range(0, cfg.create_config['polls'][poll_type]['count']):
            poll_template = deepcopy(cfg.create_config['polls'][poll_type]['template'])
            poll_template['questions'][0]['question'] = poll_template['questions'][0]['question'] % cfg.poll_entities[i]
            poll_template['description'] = poll_template['description'] % i
            rest_path = "/entity/polls/"
            poll_id = post_retrieve(rest_path, poll_template, key="id")
            poll_ids.append(poll_id)

def create_taganomy(numevents, attach=True):
    numtags = cfg.create_config['tags_per_event']
    totaltags = cfg.random_tags

    for i in range(0, numevents):
        my_tag_payload = tag_payload.copy()

        rand_ids = sample(xrange(1, len(totaltags)), numtags)
        event_tags = [totaltags[x] for x in rand_ids]
        rest_path = "/entity/tags/"
        my_tag_payload['category'] = "Event_" + str(i)
        my_tag_payload['tags'] = event_tags
        tid = post_retrieve(rest_path, my_tag_payload, key="id")
        taganomy_ids.append(tid)

        if attach:
            event_related_payload["related"] = [{"ids": [tid], "type": "e_category"}]
            event_id = event_ids[i]
            rest_path = "/entity/events/" + str(event_id) + "/"
            event_id = put_retrieve(rest_path, event_related_payload, "id")

def create_exhibitors(numevents, attach=False):
    numexb = cfg.create_config['exhibitors']
    totalexb = cfg.random_emails

    for i in range(0, numevents):

        rand_ids = sample(xrange(1, len(totalexb)), numexb)
        exbs = [totalexb[x] for x in rand_ids]
        rest_path = "/entity/exhibitors/"
        for exb in exbs:
            name = re.match("(.*?)\@", exb)
            name = name.group(1)
            payload = {'name': name, 'email': exb}
            eid = post_retrieve(rest_path, payload, key="id")
            exb_ids.append({'id': eid, 'email': exb, 'name': 'name'})


        if attach:
            eids = map(lambda x:x['id'], exb_ids)
            event_related_payload["related"] = [{"ids": eids, "type": "e_exhibitor"}]
            event_id = event_ids[i]
            rest_path = "/entity/events/%s/" % str(event_id)
            event_invite_payload = {"ids": eids}

            try:
                event_id = put_retrieve(rest_path, event_related_payload, "id")
                invite_res = post_retrieve(rest_path+"invite_exhibitors/", event_invite_payload, key="id")
            except:
                pass
            for exb in exb_ids:
                rest_path = "/users/registration/"
                my_user_payload = user_register_payload.copy()
                my_user_payload['username'] = "exhibitor_" + str(exb['id'])
                my_user_payload['email'] = exb['email']
                my_user_payload['first_name'] = exb['name']
                my_user_payload['last_name'] = exb['name']
                my_user_payload['user_type'] = 4
                exhibitor_credentials.append({'username': my_user_payload['username']})
                try:
                    token = post_retrieve(rest_path, my_user_payload, headers={"Content-type": "application/json"}, key="key")
                except:
                    print "User Already exists"



key = post_retrieve("/users/registration/",{'username':'kappu.biz', 'email':'kappu.biz@gmail.com', 'first_name':'Kappu', 'last_name':'Biz', 'password1':'a1b2c3d4', 'password2': 'a1b2c3d4', 'user_type':2}, key="key")
token = post_retrieve("/users/login/", user_login_payload, key='token')
headers['Authorization'] = "Token " + token
#Create Speakers
numspeakers = cfg.create_config['speakers']
speakerfile = cfg.create_config['speaker_file']
create_speakers(numspeakers, speakerfile)

numsponsors = cfg.create_config['sponsors']
sponsorfile = cfg.create_config['sponsor_file']
create_sponsors(numsponsors, sponsorfile)

create_polls()

numevents = cfg.create_config['events']
create_events(numevents)

create_taganomy(numevents, attach=True)


agenda_items = cfg.create_config['agenda_items']
for evt in event_ids:
    rest_path = "/entity/events/" + str(evt)
    start_date = get_retrieve(rest_path, "start")
    end_date = get_retrieve(rest_path, "end")
    speakers = get_retrieve(rest_path, "speakers")
    create_agenda(agenda_items, evt,start_date, end_date, speakers)

create_exhibitors(numevents, attach=True)

numcampaigns = cfg.create_config['campaigns']
campaignfile = cfg.create_config['campaign_file']
create_sponsors(numcampaigns, campaignfile, type="campaign", attach=True)


numusers = cfg.create_config['num_users']
userlist = []
for i in range(numusers):
    u = User()
    u.onboard_user()
    map(lambda x:u.entity_join(x, entity_type='EVT'), event_ids)











