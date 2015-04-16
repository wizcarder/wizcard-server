AWSHOSTS=['ec2-52-74-128-1.ap-southeast-1.compute.amazonaws.com','ec2-52-74-60-152.ap-southeast-1.compute.amazonaws.com']
ALLHOSTS = {
	'test':{
		'LOCATIONSERVER': ['ec2-52-74-128-1.ap-southeast-1.compute.amazonaws.com'],
		'WIZSERVER':AWSHOSTS,
                'NGINX':AWSHOSTS
	},
        'dev':{
            'LOCATIONSERVER':['localhost'],
            'WIZSERVER':['localhost'],
            'NGINX':['localhost']
        }
}
