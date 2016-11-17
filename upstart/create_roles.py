import boto3
from wizcard import instances
from lib.preserialize import serialize
import pprint
RUNHOSTS=dict()

eclient = boto3.client('ec2')

allhosts = eclient.describe_instances()

def create_mapping():
	hostmap = dict()
	hostmap['localhost'] = 'localhost'

	for resv in allhosts['Reservations']:
		for inst in resv['Instances']:
			hostmap[inst['PublicDnsName']] = inst['PrivateIpAddress']
	return hostmap


hostmap = create_mapping()

for env in instances.ALLHOSTS.keys():
	RUNHOSTS[env] = {}
	for role in instances.ALLHOSTS[env].keys():
		RUNHOSTS[env][role] = []
		for hosts in instances.ALLHOSTS[env][role]:
			host = hostmap[hosts]
			if role == "MEMCACHE":
				host = hostmap[hosts] + ":11211"
			RUNHOSTS[env][role].append(host)

#pp = pprint.PrettyPrinter()

#printrunhosts = serialize.serialize(RUNHOSTS)
runhosts =  pprint.pformat(RUNHOSTS)
print "RUNHOSTS = %s" % runhosts



		






