#!/usr/bin/env fab
from fabric.api import *
from fabric.utils import *
from fabric.contrib.files import exists
from contextlib import contextmanager
from wizcard import instances
import re
import logging

logging.basicConfig(level=logging.INFO)
env.venv = '/home/'+env.runuser+'/'+env.henv
env.activate = 'source /home/' +env.runuser+'/'+ env.henv+'/bin/activate'
env.installroot = '/home/'+env.runuser+'/' + env.henv + '.env/'
env.awskey = './certs/stagewizcard.pem'
env.gitkey = '/home/ubuntu/.ssh/id_rsa'
if env.henv != 'dev':
    env.key_filename = ['./certs/prodindia.pem']
else:
    env.key_filename = ['/home/anand/testenv/wizcard-server/certs/wizcard-default.pem']
    env.key_filename = ['./certs/wizcard-default.pem']
env.gitkey = '/home/ubuntu/.ssh/id_rsa'
#env.henv = 'dev'
#env.function = 'WIZSERVER'

@task
def set_hosts():
    with virtualenv():
    	env.hosts = instances.ALLHOSTS[env.henv][env.function]
        print env.hosts

@task
def check_services():
    run("%s/upstart/check_process.sh" % env.installroot)

@task
def getawsip():
    awshost = run("hostname")
    awsip = re.sub('ip-','',awshost)
    awsip = re.sub('-','.',awsip)

    return awsip



@contextmanager
def virtualenv():
	with cd(env.venv):
		with prefix(env.activate):
			yield

def aptgets(name="all"):
	if name == "all":
                run("echo deb \"http://us.archive.ubuntu.com/ubuntu/ trusty multiverse\" | sudo tee -a /etc/apt/sources.list")
                run("echo deb-src \"http://us.archive.ubuntu.com/ubuntu/ trusty multiverse\" | sudo tee -a /etc/apt/sources.list")
                run("echo deb \"http://us.archive.ubuntu.com/ubuntu/ trusty-updates  multiverse\" | sudo tee -a /etc/apt/sources.list")
                run("echo deb-src \"http://us.archive.ubuntu.com/ubuntu/ trusty-updates multiverse\" | sudo tee -a /etc/apt/sources.list")
		run("sudo apt-get -q -y update")
                run("sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev  python-tk")
                run("sudo apt-get install fonts-roboto")
		run("sudo apt-get -q -y install python-pip")
                run ("sudo apt-get install libpq-dev python-dev")
#		run("sudo apt-get -q -y install libmysqlclient-dev")
#		run("sudo apt-get -q -y install  mysql-client-core-5.6")
                run("sudo apt-get -q -y install postgresql-client")
		run("sudo apt-get -q -y install python-virtualenv")
                run("sudo apt-get -q -y install libjpeg-dev libpng-dev zlib1g-dev libopenjpeg-dev openjpeg-tools")
		run("sudo apt-get -q -y install python-dev")
		run("sudo apt-get -q -y install git")
                run("sudo apt-get -q -y install ntp")
		run("sudo apt-get -q -y install rabbitmq-server")
                run("sudo rabbitmq-plugins enable rabbitmq_management")
		run("sudo apt-get -q -y install libssl-dev")
		run("sudo apt-get -q -y install memcached")
	        run("sudo apt-get -q -y install libfreetype6-dev ")
		run("sudo apt-get -q -y install libffi-dev libxml2 libxml2-dev  libxslt1-dev")
		run("sudo apt-get -q -y install nginx")
		run("sudo apt-get -q -y install monit")
#                run("sudo ntpdate -s ntp.ubuntu.com")
	else:
		run("sudo apt-get -q -y install %s" % name)

def installpackage(name=env.installroot + "/req.txt"):
        if run("test -d %s" % env.venv).succeeded:
		with virtualenv():
			run("pip install   -r %s" % name)
	else:
		run("mkdir %s" % env.venv)
		installpackage()


@task
def gitcloneupdate():
    repo = 'git@github.com:wizcarder/wizcard-server.git'
    if env.henv == 'dev':
        with settings(warn_only=True):
         local("scp -i %s %s %s@%s:/home/%s/.ssh/id_rsa" % (env.key_filename[0],env.gitkey,env.runuser,env.host,env.runuser)) 

    with settings(warn_only=True):
        if run("test -d %s" % env.installroot).failed:
            run("git clone git@github.com:wizcarder/wizcard-server.git  %s" % env.installroot)
        else:
            with cd(env.installroot):
             run("cd %s && git checkout master && git pull origin master" % env.installroot)

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
        intip = getawsip()
	with settings(warn_only=True):
		with cd(env.installroot):
			if run("test -d %s" % path).failed:
				run("mkdir log")
                with virtualenv():
		    with cd(env.installroot):
                        #                        run("python manage.py syncdb")
			if env.henv != 'prod':
	                        run("python manage.py makemigrations")
                        run("python manage.py migrate")

                        #append_settings()
#                        run("cp wizcard/awstest_settings.py wizcard/settings.py")
			init_upstart()
                        init_monit()

@task
def init_monit():
	with cd(env.installroot):
            with settings(warn_only=True):
                intip = getawsip()
		run("sudo cp monit/* /etc/monit/conf.d/")
                for files in ("/etc/monit/conf.d/wizserver", "/etc/monit/conf.d/beatcelery", "/etc/monit/conf.d/celeryworker", "/etc/monit/conf.d/celeryflower","/etc/monit/conf.d/twistd", "/etc/monit/conf.d/memcached", "/etc/monit/conf.d/recogenfull", "/etc/monit/conf.d/recogentrigger" ):
                    edit_file("XXX",env.installroot,files)
                    edit_file("HOSTIP",intip,files)
		run("sudo rm /etc/monit/conf.d/*.bak")
		run("sudo monit reload")

@task
def init_upstart():
	with cd(env.installroot):
            with settings(warn_only=True):
                intip = getawsip()
		run("sudo cp upstart/*.conf /etc/init")
                for files in ("/etc/init/wizserver.conf", "/etc/init/celerybeat.conf", "/etc/init/celeryworker.conf", "/etc/init/locationjob.conf", "/etc/init/celeryflower.conf","/etc/init/twistd.conf", "/etc/init/recogenfull.conf", "/etc/init/recogentrigger.conf"):
                    edit_file("env host=xxx","env host="+intip,files)
                    edit_file("env basedir=xxx","env basedir="+env.installroot,files)
                    edit_file("env runuser=xxx","env runuser="+env.runuser,files)
                    edit_file("env venv=xxx","env venv="+env.venv,files)
                    edit_file("env WIZRUNENV=xxx","env WIZRUNENV="+env.henv,files)
                edit_file("env host=xxx", "env host="+intip,"/etc/init/memcached.conf")
                run("sudo cp upstart/%s/wizserver /etc/nginx/sites-enabled" % env.henv)
                edit_file("SERVERIP", intip, "/etc/nginx/sites-enabled/wizserver")
                edit_file("127.0.0.1", intip, "/etc/memcached.conf")
                run("sudo rm /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/wizserver.bak")

def edit_file(find,replace,efile):

    tmp_find = re.escape(find)
    tmp_replace = re.escape(replace)

    run("sudo sed -i.bak 's/%s/%s/' %s" % (tmp_find,tmp_replace,efile))


@task
def stopservices():
	stoplocationservice()
	stopwizserver()

def startnginx():
    run("sudo /etc/init.d/nginx restart")

def stopnginx():
    run("sudo /etc/init.d/nginx stop")

def startreco():
    with virtualenv():
	with cd(env.installroot):
            run("sudo service recogenfull start basedir=%s venv=%s WIZRUNENV=%s runuser=%s PYTHONPATH=$PYTHONPATH:%s" % (env.installroot,env.venv,env.henv,env.runuser,env.installroot),pty=False)
            run("sudo service recogentrigger start basedir=%s venv=%s WIZRUNENV=%s runuser=%s PYTHONPATH=$PYTHONPATH:%s" % (env.installroot,env.venv,env.henv,env.runuser,env.installroot),pty=False)

def startcelery():
    with virtualenv():
	with cd(env.installroot):
            run("sudo service celeryworker start basedir=%s venv=%s WIZRUNENV=%s runuser=%s PYTHONPATH=$PYTHONPATH:%s" % (env.installroot,env.venv,env.henv,env.runuser,env.installroot),pty=False)
            run("sudo service celerybeat start basedir=%s venv=%s WIZRUNENV=%s runuser=%s PYTHONPATH=$PYTHONPATH:%s" % (env.installroot,env.venv,env.henv,env.runuser,env.installroot),pty=False)
            run("sudo service celeryflower start basedir=%s venv=%s WIZRUNENV=%s runuser=%s PYTHONPATH=$PYTHONPATH:%s" % (env.installroot,env.venv,env.henv,env.runuser,env.installroot),pty=False)
            run("ps auxww | grep celery")

def startrabbit():
    with virtualenv():
        with cd(env.installroot):
		run("sudo rabbitmqctl stop_app")
		run("sudo rabbitmqctl reset")
		run("sudo rabbitmqctl start_app")
		fastprint("\nRunning rabbitmqconfig.sh===================================\n")
		run("pwd;sudo ./rabbitmqconfig.sh")
        	run("sudo service rabbitmq-server restart")
		run("ps auxww | grep rabbit")

def startlocation():
    with virtualenv():
        with cd(env.installroot):
            run("sudo service locationjob start basedir=%s venv=%s WIZRUNENV=%s runuser=%s PYTHONPATH=$PYTHONPATH:%s" % (env.installroot,env.venv,env.henv,env.runuser,env.installroot),pty=False)
	    run("ps auxww | grep tree_state")

@task
def startservices():
    startmemcached()
    startrabbit()
    startcelery()
    startlocation()
#    starttwistd()
    startgunicorn()
    startnginx()



@task
def startmemcached():
    run("sudo /etc/init.d/memcached start")

@task
def stopmemcached():
    with settings(warn_only=True):
        run("sudo /etc/init.d/memcached stop")

@task
def starttwistd():
    with virtualenv():
        with cd(env.installroot):
            #            run("twistd -r select web --class=pyapns.server.APNSServer --port=7077", pty=False)
            run("sudo service twistd start basedir=%s venv=%s WIZRUNENV=%s runuser=%s" % (env.installroot,env.venv,env.henv,env.runuser), pty=False)


@task
def stoptwistd():
    with virtualenv():
        with cd(env.installroot):
            run("sudo service twistd stop")

@task
def startlocationservice():
    with shell_env(WIZRUNENV=env.henv):
        startmemcached()
        startrabbit()
        startlocation()
	

@task
def startwizserverinstance():
    startmemcached()
    startrabbit()
    startcelery()
    startgunicorn()
#    starttwistd()
    startnginx()
#    startreco()

@task
def startgunicorn():

	with virtualenv():
		with cd(env.installroot):
			fastprint("\nRunning gunicorn server on %s===================================\n" % env.host)
                        run("sudo service wizserver start host=%s basedir=%s venv=%s runuser=%s WIZRUNENV=%s PYTHONPATH=$PYTHONPATH:%s" % (getawsip(),env.installroot,env.venv,env.runuser,env.henv,env.installroot), pty=False)
			run("ps auxww | grep gunicorn")
			
def freeze():
	with virtualenv():
		run('pip freeze')
@task
def stoplocationservice():
    with settings(warn_only=True):
	run("sudo service locationjob stop")
        stopmemcached()
@task
def stopwizserver():
    with settings(warn_only=True):
	run("sudo service wizserver stop")
	run("sudo service celerybeat stop")
	run("sudo service celeryworker stop")
	run("sudo service celeryflower stop")
#	run("sudo service recogenfull stop")
#	run("sudo service recogentrigger stop")
        stopmemcached()
#        stoptwistd()
        stopnginx()

	
@task
def updaterestart():
    gitcloneupdate()
    restart()

@task
def restart():
    createvirtualenv()
    if (env.function == "WIZSERVER"):
	stopwizserver()
	startwizserverinstance()
    elif (env.function == "LOCATIONSERVER"):
	stoplocationservice()
	startlocationservice()
		
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
def checkjobstatus():
    if env.function == "LOCATIONSERVER":
        run("sudo service locationjob status")

    if env.function == "WIZSERVER":
        run("sudo service celeryworker status")
        run("sudo service wizserver status")
        run("sudo service celerybeat status")
        run("sudo service rabbitmq-server status")
        run("sudo service recogenfull status")
        run("sudo service recogentrigger status")

@task
def deploy():

    with shell_env(WIZRUNENV=env.henv):

	if (env.function == "WIZSERVER"):
            deploywizserver()
        elif (env.function == "LOCATIONSERVER"):
            deploylocation()
        else:
            deployall()
