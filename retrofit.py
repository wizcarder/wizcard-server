import os,sys

proj_path="/home/ubuntu/test.env"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wizcard.settings")
from wizserver import verbs
from wizserver import fields
from wizcardship.models import WizConnectionRequest
from base.cctx import *
from lib.preserialize.serialize import serialize
sys.path.append(proj_path)
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

RUNENV="test"

wc=map(lambda x: x.id,WizConnectionRequest.objects.all().filter(cctx='', status=verbs.ACCEPTED))

for tid in wc:
	wcr = WizConnectionRequest.objects.get(id=tid)
	ctx = ConnectionContext(asset_obj=wcr.from_wizcard,description="", connection_mode=verbs.INVITE_VERBS[verbs.WIZCARD_CONNECT_T])
	ctx.description = "Re-added to Rolodex"

	pctx = serialize(ctx.context,**fields.cctx_wizcard_template)
	wcr.cctx = ctx
	wcr.save()
	print pctx

wc=WizConnectionRequest.objects.all()

for twc in wc:
	from_wc = twc.from_wizcard

	print "Changing context for " + str(twc)

	twc.cctx.context['asset_obj'] = from_wc

	twc.save()

	pctx=serialize(twc.cctx.context,**fields.cctx_wizcard_template)
	print pctx

	
	
