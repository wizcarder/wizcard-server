import requests
import sys
import simplejson as json
import event_config as cfg
from random import randint, sample
from datetime import datetime, timedelta
from copy import deepcopy
from api_test import User
import messages



headers = {"Content-type": "application/json"}
speaker_ids = []
sponsor_ids = []
campaign_ids = []
agenda_ids = []
event_ids = []
poll_ids = []
filemap = {'speaker':'ceos.tsv', 'sponsor': 'companies.tsv', 'campaign':'companies.tsv'}
#User Login
user_payload = {"username": "kappu.biz", "password": "a1b2c3d4"}

media_payload = {"media_element": "", "media_type": "", "media_sub_type": ""}
speaker_payload = {"name":"", "designation":"", "company":"","ext_fields":{}, "email":"a@b.com", "related":[]}
sponsor_payload = {"name":"", "caption":"", "website": "http://getwizcard.com", "ext_fields":{"linkedin": "http://www.linkedin.com", "twitter": "http://www.twitter.com"}, "phone": "+180090010001", "email":"a@b.com", "description": "Campaign description is here", "address":"1234, Some Lane, Some City, Some Country"}
agenda_payload = {"items":[]}
event_payload = {"name":"", "description":"", "venue": "Pragati Maidan", "location":{'lat':"", 'lng':""}, "start":"", "end":"", "related":[], "website":"http://www.getwizcard.com", "email":"a@b.com"}
#server = "http://test.wizcard.be:8080/"
server = "http://localhost:8000"

def post_retrieve(rest_path, payload, rkey):

    request_url = server + rest_path
    resp = requests.post(request_url, json=payload, headers=headers, timeout=5)
    resp_dict = resp.json()
    return resp_dict[rkey]

def get_retrieve(rest_path, rkey):
    request_url = server + rest_path
    resp = requests.get(request_url, headers=headers, timeout=5)
    resp_dict = resp.json()
    return resp_dict[rkey]


def create_media(url, media_type='IMG', media_sub_type='ROL'):
    media_payload['media_element'] = url
    media_payload['media_type'] = media_type
    media_payload['media_sub_type'] = media_sub_type
    media_id = post_retrieve("/entity/media/", media_payload, "id")
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
        speaker_id = post_retrieve("/entity/speakers/", speaker_payload, "id")
        speaker_ids.append(speaker_id)


def create_sponsors(num, file, type="sponsors"):
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
        sponsor_id = post_retrieve("/entity/"+type+"/", sponsor_payload, "id")
        if type == 'campaigns':
            campaign_ids.append(sponsor_id)
        else:
            sponsor_ids.append(sponsor_id)

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

        event_id = post_retrieve("/entity/events/", event_payload, "id")
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
        agenda_id = post_retrieve(rest_path, agenda_payload, "id")

        agenda_ids.append(agenda_id)

def create_polls(evt):
    for poll_type in cfg.create_config['polls']:
        for i in range(0, cfg.create_config['polls'][poll_type]['count']):
            poll_template = deepcopy(cfg.create_config['polls'][poll_type]['template'])
            poll_template['questions'][0]['question'] = poll_template['questions'][0]['question'] % cfg.poll_entities[i]
            poll_template['description'] = poll_template['description'] % i
            rest_path = "/entity/polls/"
            poll_id = post_retrieve(rest_path, poll_template, "id")
            poll_ids.append(poll_id)

#post_retrieve("/users/registration/",{'username':'kappu.biz', 'email':'kappu.biz@gmail.com', 'first_name':'Kappu', 'last_name':'Biz', 'password1':'a1b2c3d4', 'password2': 'a1b2c3d4', 'user_type':2}, 'token')
token = post_retrieve("/users/login/", user_payload, 'token')
headers['Authorization'] = "Token " + token
#Create Speakers
numspeakers = cfg.create_config['speakers']
speakerfile = cfg.create_config['speaker_file']
create_speakers(numspeakers, speakerfile)

numsponsors = cfg.create_config['sponsors']
sponsorfile = cfg.create_config['sponsor_file']
create_sponsors(numsponsors, sponsorfile)

numcampaigns = cfg.create_config['campaigns']
campaignfile = cfg.create_config['campaign_file']
create_sponsors(numcampaigns, campaignfile, type="campaigns")

numevents = cfg.create_config['events']
create_events(numevents)

agenda_items = cfg.create_config['agenda_items']
for evt in event_ids:
    rest_path = "/entity/events/" + str(evt)
    start_date = get_retrieve(rest_path, "start")
    end_date = get_retrieve(rest_path, "end")
    speakers = get_retrieve(rest_path, "speakers")
    create_agenda(agenda_items, evt,start_date, end_date, speakers)


for evt in event_ids:
    create_polls(evt)

numusers = cfg.create_config['num_users']
userlist = []
for i in range(numusers):
    u = User()
    u.onboard_user()
    map(lambda x:u.entity_join(x, entity_type='EVT'), event_ids)











