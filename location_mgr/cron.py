import location_mgr
from django_cron import cronScheduler as cron
from location_mgr.models import Tick
cron.register(Tick)
