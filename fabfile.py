from fabric.api import *
from fabric.utils import *
from contextlib import contextmanager
env.directory = '/home/ubuntu/stage'
env.activate = 'source /home/ubuntu/stage/bin/activate'

@contextmanager
def virtualenv():
	with cd(env.directory):
		with prefix(env.activate):
			yield

def aptgets(name="all"):
	if name == "all":
		run("sudo apt-get -q -y update")
		run("sudo apt-get -q -y install python-pip")
		run("sudo apt-get -q -y install libmysqlclient-dev")
		run("sudo apt-get -q -y install  mysql-client-core-5.6")
		run("sudo apt-get -q -y install python-virtualenv")
		run("sudo apt-get -q -y install python-dev")
		run("sudo apt-get -q -y install git")
		run("sudo apt-get -q -y install rabbitmq-server")
		run("sudo apt-get -q -y install libssl-dev")
		run("sudo apt-get -q -y install libffi-dev libxml2 libxml2-dev  libxslt1-dev")
		run("sudo apt-get -q -y install nginx")
	else:
		run("sudo apt-get -q -y install %s" % name)

def installpackage(name="/home/ubuntu/latest/req.txt"):
	path = "/home/ubuntu/stage"
        if run("test -d %s" % path).succeeded:
		run("source %s/bin/activate && pip install -q  -r /home/ubuntu/latest/req.txt" % path)
	else:
		run("mkdir %s" % path)
		installpackage()
#	run("pip install -r %s" % name)


def gitcloneupdate(code_dir="/home/ubuntu/latest"):
    repo = 'git@github.com:wizcarder/wizcard-server.git'

    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone git@github.com:wizcarder/wizcard-server.git  %s" % code_dir)
    with cd(code_dir):
        run("cd %s && git pull" % code_dir)

def localgitpullfile(code_dir="/home/anand/latest"):
    repo = 'git@github.com:wizcarder/wizcard-server.git'

    with settings(warn_only=True):
        if local("test -d %s" % code_dir).failed:
            local("git clone git@github.com:wizcarder/wizcard-server.git  %s" % code_dir)
    with cd(code_dir):
        local("cd %s && git pull" % code_dir)



#fab pullsnapshot(tarpath)

def createvirtualenv(path="/home/ubuntu/stage"):
    with settings(warn_only=True):
        if run("test -d %s" % path).failed:
		run("virtualenv %s --prompt=VIRTUAL:" % path)

def postinstall(hostenv="stage"):
	path = "/home/ubuntu/latest/log"
	with settings(warn_only=True):
		if run("test -d %s" % path).failed:
			run("cd /home/ubuntu/latest && mkdir log")
		run("cd /home/ubuntu/latest && mv wizcard/awstest_settings.py wizcard/settings.py")

def startservices():
	with virtualenv():
		with cd("/home/ubuntu/latest"):
			run("sudo service rabbitmq-server restart")
			fastprint("\nRunning rabbitmqconfig.sh===================================\n")
			run("sudo sh ./rabbitmqconfig.sh")
			run("ps auxww | grep rabbit")
			fastprint("\nRunning location server===================================\n")
			run("python  ./location_service/tree_state.py --g&")
			run("ps auxww | grep tree_state")
			fastprint("\nRunning celery server===================================\n")

			run("sh ./startcelery.sh", pty=False)
			run("ps auxww | grep celery")
			fastprint("\nRunning gunicorn server===================================\n")
			run("gunicorn  --daemon wizcard.wsgi:application", pty=False)
			run("ps auxww | grep gunicorn")
			
def runservice():
	with virtualenv():
		with cd("/home/ubuntu/latest"):
			run("sh runservice")

def freeze():
	with virtualenv():
		run('pip freeze')

def stopservices():
	run("sudo service rabbitmq-server stop")
	run("cd /home/ubuntu/latest; kill -TERM $(cat celeryd.pid)")
	run("pkill gunicorn")
		
def deploy():
	fastprint("\nRunning aptgets===================================\n")
	aptgets()
	fastprint("\ndone aptgets===================================\n")
	fastprint("\nRunning aptgets===================================\n")
	gitcloneupdate()
	fastprint("\nDone gitcloneupdate===================================\n")
	fastprint("\nRunning createvirtualenv===================================\n")
	createvirtualenv()
	fastprint("\nDone createvirtualenv===================================\n")
	fastprint("\nRunning installpackage===================================\n")
	installpackage()
	fastprint("\nDone installpackage===================================\n")
	fastprint("\nRunning postinstall===================================\n")
	postinstall()
	fastprint("\nDone postinstall===================================\n")
	fastprint("\nRunning startservices===================================\n")
	stopservices()
	startservices()
	fastprint("\nDone aptgets===================================\n")
	fastprint("\nRunning aptgets===================================\n")
#	runtests()


	
	
	

	


