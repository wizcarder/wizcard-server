import weakref
import pdb
import bisect_wrapper
from operator import itemgetter
from pprint import pprint

class Timer:
    _timerlist = bisect_wrapper.SortedCollection(key=itemgetter(1))
    _id2obj_dict = weakref.WeakValueDictionary()

    @classmethod
    def id2obj(cls, oid):
        return Timer._id2obj_dict[oid]

    @classmethod
    def tick(cls):
        for index, item in enumerate(Timer._timerlist):
            if item[0].timeout_delta:
                #first non zero timeout_delta
                item[0].timeout_delta -= 1
                break
    
    @classmethod
    def has_expiry(cls):
        if Timer._timerlist and not Timer._timerlist[0][0].timeout_delta:
            return True
        return False

    @classmethod
    def process_timer(cls, count=0):
        #record a tick
        Timer.tick()
        #stay at the head
        index = 0
        while(Timer.has_expiry()):
            t = list(Timer._timerlist).pop(index)
            pprint(t)
            t[0].remove_index(index) 
      
    @classmethod
    def show_timer(cls):
        print("Timer List:")
        pprint(list(Timer._timerlist))

    @classmethod
    def show_idmap(cls):
        print("ID2OBJ map:")
        pprint(dict(Timer._id2obj_dict))

    def __init__(self, timeout, callback_fn, ):
        self.timeout = timeout
        self.timeout_delta = timeout
        self.adjusted_timeout = timeout
        self.id = id(self)
        Timer._id2obj_dict[self.id] = self

    def __repr__(self):
	    return '[' + 'id:'+str(self.id) + ' timeout:'+ str(self.timeout) + ' adjusted timeout:'+ str(self.adjusted_timeout) + ' timeout_delta:'+str(self.timeout_delta) + ']'

    def remove_index(self, index):
        Timer._timerlist.remove_index(index)
        del Timer._id2obj_dict[self.id]
        
    def is_expired(self):
        return not self.timeout_delta
        
    def start(self):
        self.adjusted_timeout = self.timeout if not len(Timer._timerlist) else self.timeout + Timer._timerlist[0][0].adjusted_timeout - Timer._timerlist[0][0].timeout_delta
        try:
            prev_index = Timer._timerlist.find_le_index(self.adjusted_timeout)
            self.timeout_delta = self.adjusted_timeout - Timer._timerlist[prev_index][0].adjusted_timeout
        except ValueError:
            prev_index = -1 

        if (len(Timer._timerlist) -1) > prev_index and len(Timer._timerlist) != 0:
            #inserting in the middle, adjust delta of prev+1
            Timer._timerlist[prev_index+1][0].timeout_delta = Timer._timerlist[prev_index+1][0].adjusted_timeout - self.adjusted_timeout
        
        Timer._timerlist.insert_right((self, self.adjusted_timeout))
        return self.id

    def stop(self):
        index = Timer._timerlist.index((self, self.adjusted_timeout))
        if (len(Timer._timerlist) - 1) > index:
            #removing non-last, adjust next guys delta
            Timer._timerlist[index+1][0].timeout_delta += Timer._timerlist[index][0].timeout_delta
        self.pop(index)

    def reset(self):
        self.stop()
        self.start()
