from fabric.api import *
def hello(who="host"):
	run("uname -a")

def aptgets(name="all"):
	if name == "all":
		run("sudo apt-get -y update")
		run("sudo apt-get -y install python-pip")
		run("sudo apt-get -y install libmysqlclient-dev")
		run("sudo apt-get -y install python-virtualenv")
		run("sudo apt-get -y install python-dev")
		run("sudo apt-get -y install git")
		run("sudo apt-get -y install rabbitmq-server")
		run("sudo apt-get -y install libssl-dev")
		run("sudo apt-get -y install libffi-dev libxml2 libxml2-dev  libxslt1-dev")
		run("sudo apt-get nginx")
	else:
		run("sudo apt-get -y install %s" % name)

def installpackage(name="/home/ubuntu/latest/req.txt"):
	path = "/home/ubuntu/stage"
        if run("test -d %s" % path).failed:
		run("source %s/bin/activate && pip install -r /home/ubuntu/latest/req.txt" % path)
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

def postinstall():
	path = "/home/ubuntu/latest/log"
	with settings(warn_only=True):
		if run("test -d %s" % path).failed:
			run("cd /home/ubuntu/latest && mkdir log")

def deploy():
	aptgets()
	gitcloneupdate()
	createvirtualenv()
	installpackage()
	postinstall()
#	startservices()
#	runtests()


	
	
	

	


