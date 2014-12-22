from pyapns import configure, provision, notify, feedback
configure({'HOST':'http://localhost:7077/'})
provision('com.beta.wizcard', open('/Users/aammundi/projects/git/wizcard-server/certs/wizcard_ios_apns_production.pem').read(), 'production')
#provision('com.beta.wizcard', open('/Users/aammundi/projects/git/wizcard-server/certs/wizcard_ios_apns_dev.pem').read(), 'sandbox')
#notify('com.beta.wizcard', '5f660dfacba5f8222946811724e012e2a6887460768083b39277d7e259b1675e', {'aps':{'alert':'Hello!'}})
notify('com.beta.wizcard', '6c4f3dcb31cb45bdaf399206ea065b9795bee698cd56a60bcd40ee336741d4dd', {'aps':{'alert':'Hello!'}})

