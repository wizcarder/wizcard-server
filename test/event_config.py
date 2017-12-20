mcr_poll = { "description" : "Poll %d",
             "questions": [{
                "question":"Did you like the %s today?",
                "question_type": 'MCR',
                "ui_type": 'SEL',
                "single_answer": True,
                "extra_text" : False,
                "choices" : [{"question_key": "A", "question_value":"Loved it"},
                         {"question_key": "B", "question_value":"Nothing to complain"},
                         {"question_key": "C", "question_value": "could have been better"},
                         {"question_key": "D", "question_value":"Should have gone outside"}
                        ]
            }]
        }

scl_poll = { "description" : "Poll %d",
             "questions": [{
                "question":"Rate the %s",
                "question_type": 'SCL',
                "ui_type": 'SLD',
                "single_answer": True,
                "extra_text" : False,
                "choices" : [{'low':0, 'high': 5}]
            }]
        }

tof_poll = { "description" : "Poll %d",
             "questions": [{
                "question":"Did you like the %s",
                "question_type": 'TOF',
                "ui_type": 'RAD',
                "single_answer": True,
                "extra_text" : False,
                "choices" : [{"True": "Yes", "False":"No"}]
            }]
        }


txt_poll = {"description" : "Poll %d",
             "questions": [{
                "question":"How was the %s?",
                "question_type": 'TXT',
                "ui_type": 'TEX',
                "single_answer": True,
                "extra_text" : True,
                "choices" : []
            }]
            }

poll_entities = ['breakfast', 'lunch', 'talk', 'panel discussion', 'arrangements']
create_config = {
                    'events':  2,
                    'speakers' : 5,
                    'sponsors': 5,
                    'campaigns' : 1,
                    'agenda_items': 1,
                    'event_media' : 1,
                    'campaign_media': 1,
                    'speaker_file' : './/test/ceos.tsv',
                    'sponsor_file' : './test/sponsors.tsv',
                    'campaign_file' : './test/sponsors.tsv',
                    'event_interval' : 2,
                    'polls' : {
                        'MCR' : {'count':2, 'template' : mcr_poll},
                        'SCL' : {'count':2, 'template': scl_poll},
                        'TOF' : {'count': 2, 'template' : tof_poll},
                        'TXT' : {'count': 2, 'template': txt_poll}
                    },
                    'num_users' : 2
}





random_locations = [{'venue': 'JW Marriot, Bangalore', 'lat':12.9720112,'lng': 77.5926823},{'venue': 'Taj Coromandel, Chennai', 'lat':13.0585208, 'lng':80.245048513}, {'venue': 'Pragati Maidan, New Delhi', 'lat':28.615946, 'lng': 77.237284728}, {'venue': 'Taj Lands End, Mumbai', 'lat':19.0435436, 'lng': 72.817267119}]

random_event_names = ['10,000 Latkes', '24 Carrot Seven', '25,000 Mile Stones', '29 Psalms for 29 Palms', 'A Gathering of Hunters', 'Act Out Your Age', 'Adventure Camping', 'Advertising Nauseum', 'Aesthetic Bug Gloss', 'Air Fair', 'Alanonymous', 'Amagansett Go Around', 'Amateur Barber Night', 'An Arbor Day to Remember', 'Antisocial Darwinism', 'Apathesis', 'Apocalypso', 'Aria Safari', 'Arise and Shinola', 'Aromastotle', 'Ass Texas', 'Attila the Humm', 'Aurora Tori Spelling', 'Away we golf']

random_dates = ['2018-01-18', '2018-01-29', '2018-01-30', '2018-01-31', '2018-02-08', '2018-02-15', '2018-03-02', '2018-03-15', '2018-03-21', '2018-03-28']

random_banners = ["https://blog.akshayapatra.org/wp-content/uploads/2016/04/720-X-240-Earth-Day.jpg", "http://www.nissan.com.vn/wp-content/uploads/2016/07/Banner-web-CMTKMT7-AfterSales-Banner-1920x640px-720x240.jpg", "http://aluminiuminsider.com/wp-content/uploads/2017/05/Banner-720x240.jpg", "http://www.malahinisolutions.com/images/cms-banner.jpg"]

random_videos = ["https://www.youtube.com/watch?v=8rRfqWcz-mw",
                 "https://www.youtube.com/watch?v=Kl5B6MBAntI",
                 "https://www.youtube.com/watch?v=UeG1ftTmLAg",
                 "https://www.youtube.com/watch?v=rk_qLtk0m2c",
                 "https://www.youtube.com/watch?v=ckdsJ-LaCvM",
                 "https://www.youtube.com/watch?v=txXwg712zw4",
                 "https://www.youtube.com/watch?v=gneBUA39mnI",
                 "https://www.youtube.com/watch?v=xuCn8ux2gbs",
                 "https://www.youtube.com/watch?v=2REkk9SCRn0",
                 "https://www.youtube.com/watch?v=Mh4f9AYRCZY",
                 "https://www.youtube.com/watch?v=kJQP7kiw5Fk&feature=youtu.be",
                 "http://youtu.be/kJQP7kiw5Fk",
                 "http://youtu.be/JGwWNGJdvx8",
                 "http://youtu.be/wnJ6LuUFpMo",
                 "http://youtu.be/t_jHrUE5IOk",
                 "http://youtu.be/PMivT7MJ41M",
                 "http://youtu.be/c73Cu3TQnlg",
                 "http://youtu.be/YG2p6XBuSKA",
                 "http://youtu.be/NGLxoKOvzu4",
                 "http://youtu.be/weeI1G46q0o",
                 "https://www.youtube.com/watch?v=9sg-A-eS6Ig"
                 ]

random_images = ["http://www.cutestpaw.com/wp-content/themes/cutestpaw3/fp/logo4.svg",
                 "http://www.cutestpaw.com/wp-content/uploads/2011/11/Seemly.jpg",
                 "http://www.cutestpaw.com/wp-content/uploads/2011/11/Handsome.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Puppy-scrunch-faces.jpeg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/How-is-it-so-fluffy.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Puppy-Sailor.jpeg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/The-teeniest-puppy.jpeg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Possessed.jpeg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Funny-Dog.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Pug-emoting-on-hardwood.png",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/KseVs.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Om-Nom-Nom.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Puppies.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Puppy-Planking.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Miss-You-My-Love.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/We-miss-you.jpeg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Driving-to-puppy-park.jpeg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Puppy-Power.jpeg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Puppies-Prison.jpeg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/The-teeniest-yawn-l1.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/one-for-the-weekend-l1.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/It-was-me...-I-let-the-dogs-out.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Prescription-glasses.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/oh-noes.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/hipster-puppies.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/I-DIDNT-DO-IT.jpeg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/ITS-BUSINESS-TIME.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/IM-A-PUFF.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/ALL-SMILES.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/A-FIST-FULL-OF-PUPPY.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Man-in-Black.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/a-couple-of-fluffy-puppies.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/cute-dog1.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Hot-Dogs.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Lemon.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/I-Am-Batman.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/comedian.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Four-Brothers.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/a-dogs-life.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Two-Litte-Dog.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/My-Best-Friend.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/MORE-SUPER-CUTE-ANIMALS-dogs.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/High-degree-of-adorable-cute.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/cute-puppy1.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Hamburger.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Pepsi-Dog.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/my-Adorable-Puppies.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/PeekaBoo.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Its-Winter-Time-o.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2011/11/Angel.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2012/08/s-Jack-My-Happy-Dog.jpg",
                "http://www.cutestpaw.com/wp-content/uploads/2014/01/s-Baby-seals.jpg",
                ]
