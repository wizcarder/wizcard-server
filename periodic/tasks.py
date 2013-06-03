from lib.timer import Timer
from celery import task
from celery.contrib import rdb
@task
def process_timer(count=0):
    print 'Timer Tick received'
    #record a tick
    Timer.tick()
    #stay at the head
    index = 0
    while(Timer.has_expiry()):
        t = list(Timer._timerlist).pop(index)
        print 'timer {t} timed out'.format (t=t)
        t[0].callback_fn(t[0].kwargs)
        pprint(t)
        t[0].remove_index(index) 
      
