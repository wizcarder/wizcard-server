#!/usr/bin/env fab
from fabric.api import *
from fabric.utils import *
from fabric.contrib.files import exists
from contextlib import contextmanager
from wizcard import instances
env.venv = '/home/ubuntu/stage'
env.activate = 'source /home/ubuntu/stage/bin/activate'
env.installroot = '/home/ubuntu/stage.env/'
env.henv = 'test'
#env.function = 'WIZSERVER'

@task
def set_hosts():
    with virtualenv():
    	env.hosts = instances.ALLHOSTS[env.henv][env.function]
        print env.hosts

@task
def do_ls():
    with virtualenv():
	run("ls -al > /tmp/lsout")

@contextmanager
def virtualenv():
	with cd(env.venv):
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
                run("sudo rabbitmq-plugins enable rabbitmq_management")
		run("sudo apt-get -q -y install libssl-dev")
		run("sudo apt-get -q -y install memcached")
		run("sudo apt-get -q -y install libffi-dev libxml2 libxml2-dev  libxslt1-dev")
		run("sudo apt-get -q -y install nginx")
	else:
		run("sudo apt-get -q -y install %s" % name)

def installpackage(name=env.installroot + "/req.txt"):
        if run("test -d %s" % env.venv).succeeded:
		with virtualenv():
			run("pip install   -r %s" % name)
	else:
		run("mkdir %s" % env.venv)
		installpackage()


def gitcloneupdate():
    repo = 'git@github.com:wizcarder/wizcard-server.git'

    with settings(warn_only=True):
        if run("test -d %s" % env.installroot).failed:
            run("git clone git@github.com:wizcarder/wizcard-server.git  %s" % env.installroot)
    with cd(env.installroot):
        run("cd %s && git pull" % env.installroot)

def localgitpullfile():
    repo = 'git@github.com:wizcarder/wizcard-server.git'

    with settings(warn_only=True):
        if local("test -d %s" % env.installroot).failed:
            local("git clone git@github.com:wizcarder/wizcard-server.git  %s" % env.installroot)
    with cd(env.installroot):
        local("cd %s && git pull" % env.installroot)



#fab pullsnapshot(tarpath)

def createvirtualenv():
    with settings(warn_only=True):
        if run("test -d %s" % env.venv).failed:
                prompt_str = env.henv.upper() + "ENV"
		run("virtualenv %s --prompt=%s:" % (env.venv,prompt_str))

def postinstall():
	path = env.installroot + "log"
	with settings(warn_only=True):
		with cd(env.installroot):
			if run("test -d %s" % path).failed:
				run("mkdir log")
                        #append_settings()
                        run("cp wizcard/awstest_settings.py wizcard/settings.py")
			init_upstart()

def init_upstart():
	with cd(env.installroot):
		run("sudo cp upstart/*.conf /etc/init")
                run("sudo cp upstart/%s/wizserver /etc/nginx/sites-enabled" % env.henv)
                run("sudo rm /etc/nginx/sites-enabled/default")

@task
def stopservices():
	stoplocationservice()
	stopwizserver()

def startnginx():
    run("sudo /etc/init.d/nginx restart")

def stopnginx():
    run("sudo /etc/init.d/nginx stop")

def startcelery():
    with virtualenv():
	with cd(env.installroot):
         	run("sudo service celeryworker start basedir=%s venv=%s WIZRUNENV=%s runuser=ubuntu" % (env.installroot,env.venv,env.henv),pty=False)
        	run("sudo service celerybeat start basedir=%s venv=%s WIZRUNENV=%s runuser=ubuntu" % (env.installroot,env.venv,env.henv), pty=False)
        	run("ps auxww | grep celery")

def startrabbit():
    with virtualenv():
        with cd(env.installroot):
        	run("sudo service rabbitmq-server restart")
		fastprint("\nRunning rabbitmqconfig.sh===================================\n")
		run("pwd;sudo ./rabbitmqconfig.sh")
		run("ps auxww | grep rabbit")

def startlocation():
    with virtualenv():
        with cd(env.installroot):
		run("sudo service locationjob start basedir=%s venv=%s WIZRUNENV=%s" % (env.installroot, env.venv,env.henv),pty=False)
		run("ps auxww | grep tree_state")

@task
def startservices():
    startrabbit()
    startcelery()
    startlocation()
    starttwistd()
    startgunicorn()
    startnginx()


@task
def starttwistd():
    with virtualenv():
        with cd(env.installroot):
            run("twistd -r select web --class=pyapns.server.APNSServer --port=7077", pty=False)


@task
def stoptwistd():
    with virtualenv():
        with cd(env.installroot):
            run("cat twistd.pid | xargs kill")

@task
def startlocationservice():
    with shell_env(WIZRUNENV=env.henv):
        startrabbit()
        startlocation()
	

@task
def startwizserverinstance():
    startrabbit()
    startcelery()
    startgunicorn()
    starttwistd()
    startnginx()

@task
def startgunicorn():

	with virtualenv():
		with cd(env.installroot):
			fastprint("\nRunning gunicorn server on %s===================================\n" % env.host)
			run("sudo service wizserver start host=%s basedir=%s venv=%s runuser=ubuntu WIZRUNENV=%s" % (env.host,env.installroot,env.venv,env.henv), pty=False)
			run("ps auxww | grep gunicorn")
			
def freeze():
	with virtualenv():
		run('pip freeze')
@task
def stoplocationservice():
    with settings(warn_only=True):
	run("sudo service locationjob stop")
@task
def stopwizserver():
    with settings(warn_only=True):
	run("sudo service wizserver stop")
	run("sudo service celerybeat stop")
	run("sudo service celeryworker stop")
        stoptwistd()
        stopnginx()

	
		
def deployall():
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

def deploylocation():
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
	stoplocationservice()
	startlocationservice()
	fastprint("\nDone aptgets===================================\n")
	fastprint("\nRunning aptgets===================================\n")


def deploywizserver():
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
	stopwizserver()
	startwizserverinstance()
	fastprint("\nDone aptgets===================================\n")
	fastprint("\nRunning aptgets===================================\n")
@task
def deploy():

    with shell_env(WIZRUNENV=env.henv):

	if (env.function == "WIZSERVER"):
            deploywizserver()
        elif (env.function == "LOCATIONSERVER"):
            deploylocation()
        else:
            deployall()
