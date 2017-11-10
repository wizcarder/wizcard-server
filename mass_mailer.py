import os,sys

proj_path="."

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wizcard.settings")
from lib.create_share import send_wizcard, mass_email
sys.path.append(proj_path)
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
skip_count = int(sys.argv[1])
limit = int(sys.argv[2])
id = 0 
file = "email_marketing.tsv"

with open(file) as data_file:
	for rec in data_file:
		rec=rec.strip()
		if id <= skip_count:
			print "Skipping " + rec +" " + str(id)
			id = id + 1
			continue
		mailid = "naukrilist_" + str(id)
		try:
			if id > limit:
				break
			mass_email(rec, mailid)
			print "Sending mail to " + rec + " " + mailid 
			id = id + 1
		except:
    			print "Sending mail failed for " + rec + " " + mailid
			id = id + 1
			pass
    







