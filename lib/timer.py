import weakref
import pdb
from celery import task
from lib import bisect_wrapper
from operator import itemgetter
from pprint import pprint
from multiprocessing import Process, Manager

@task
def process_timer():
    print 'Timer Tick received'
    Timer.show_timer()
    #record a tick
    Timer.tick()
    print 'Timer Tick processed'
    Timer.show_timer()
    #stay at the head
    index = 0
    while(Timer.has_expiry()):
        t = list(Timer._timerlist).pop(index)
        print 'timer {t} timed out'.format (t=t)
        t[0].callback_fn(t[0].kwargs)
        pprint(t)
        t[0].remove_index(index) 



class Timer:
    #_timerlist = bisect_wrapper.SortedCollection(key=itemgetter(1))
    #_id2obj_dict = weakref.WeakValueDictionary()
    #shared_dict['timerlist'] =  _timerlist
    #shared_dict['idmap'] = _id2obj_dict

    @classmethod
    def timer_list(cls):
        return Timer.shared_dict['timerlist']

    @classmethod
    def idmap(cls):
        return Timer.shared_dict['idmap']

    @classmethod
    def id2obj(cls, oid):
        return Timer.idmap()[oid]

    @classmethod
    def tick(cls):
        for index, item in enumerate(Timer.timerlist()):
            if item[0].timeout_delta:
                #first non zero timeout_delta
                item[0].timeout_delta -= 1
                break
    
    @classmethod
    def has_expiry(cls):
        if Timer.timerlist() and not Timer.timerlist()[0][0].timeout_delta:
            return True
        return False

    @classmethod
    def show_timer(cls):
        print("Timer List:")
        pprint(list(Timer.timerlist()))

    @classmethod
    def show_idmap(cls):
        print("ID2OBJ map:")
        pprint(dict(Timer.idmap()))

    def __init__(self, timeout, callback_fn, **kwargs):
        self.timeout = timeout
        self.timeout_delta = timeout
        self.adjusted_timeout = timeout
        self.id = id(self)
        self.callback_fn = callback_fn
        self.kwargs = kwargs
        Timer.idmap()[self.id] = self

    def __repr__(self):
	    return '[' + 'id:'+str(self.id) + ' timeout:'+ str(self.timeout) + ' adjusted timeout:'+ str(self.adjusted_timeout) + ' timeout_delta:'+str(self.timeout_delta) + ']'

    def remove_timerlist(self, index):
        Timer.timerlist().remove_index(index)

    def remove_id2obj(self, index):
        del Timer.idmap()[self.id]


    def remove_index(self, index):
        self.remove_timerlist(index)
        self,remove_id2obj(index)
        
    def is_expired(self):
        return not self.timeout_delta
        
    def start(self):
        self.adjusted_timeout = self.timeout if not len(Timer.timerlist()) else self.timeout + Timer.timerlist()[0][0].adjusted_timeout - Timer.timerlist()[0][0].timeout_delta
        try:
            prev_index = Timer.timerlist().find_le_index(self.adjusted_timeout)
            self.timeout_delta = self.adjusted_timeout - Timer.timerlist()[prev_index][0].adjusted_timeout
        except ValueError:
            prev_index = -1 

        if (len(Timer.timerlist()) -1) > prev_index and len(Timer.timerlist()) != 0:
            #inserting in the middle, adjust delta of prev+1
            Timer.timerlist()[prev_index+1][0].timeout_delta = Timer.timerlist()[prev_index+1][0].adjusted_timeout - self.adjusted_timeout
        
        Timer.timerlist().insert_right((self, self.adjusted_timeout))
        return self.id

    #stop does not remove from id2obj map
    def stop(self):
        index = Timer.timerlist().index((self, self.adjusted_timeout))
        if (len(Timer.timerlist()) - 1) > index:
            #removing non-last, adjust next guys delta
            Timer.timerlist()[index+1][0].timeout_delta += Timer.timerlist()[index][0].timeout_delta
        self.remove_timerlist(index)
        return index

    def destroy(self):
        index = self.stop()
        self.remove_id2obj(index)

    def reset(self):
        self.stop()
        self.start()
