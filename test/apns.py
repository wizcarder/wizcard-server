from pyapns import configure, provision, notify, feedback
configure({'HOST':'http://localhost:7077/'})
#provision('com.beta.wizcard', open('/Users/aammundi/projects/git/wizcard-server/certs/wizcard_ios_apns_production.pem').read(), 'production')
provision('com.beta.wizcard', open('/home/bitnami/wizcard-server/certs/wizcard_ios_apns_production.pem').read(), 'production')
#provision('com.beta.wizcard', open('/Users/aammundi/projects/git/wizcard-server/certs/wizcard_ios_apns_dev.pem').read(), 'sandbox')
#notify('com.beta.wizcard', '5f660dfacba5f8222946811724e012e2a6887460768083b39277d7e259b1675e', {'aps':{'alert':'Hello!'}})
#notify('com.beta.wizcard', '6c4f3dcb31cb45bdaf399206ea065b9795bee698cd56a60bcd40ee336741d4dd', {'aps':{'alert':'Hello!'}})
notify('com.beta.wizcard', 'a35bbb51db6a4df7c6c32dc34a57454c51efa4f3420d54b6bdb4f4a7cd064724', {'aps':{'alert':'senthil, test apns notif!'}})

