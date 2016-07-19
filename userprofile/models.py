from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from lib.pytrie import SortedStringTrie as trie
from lib.preserialize.serialize import serialize
from wizserver import fields, verbs
from location_mgr.models import location, LocationMgr
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from wizcardship.models import WizConnectionRequest, Wizcard
from virtual_table.models import VirtualTable
from dead_cards.models import DeadCards
from django.core.exceptions import ObjectDoesNotExist
from notifications.models import notify
from notifications.models import Notification
from base.cctx import ConnectionContext
from base.char_trunc import TruncatingCharField
from base.emailField import EmailField
import operator
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings
from lib import wizlib
from django.utils import timezone
import string
import random
import pdb

class UserProfileManager(models.Manager):
    def serialize_split(self, me, users):
        s = dict()
        template = fields.wizcard_template_brief

        ret = self.split_users(me, users)
        if ret.has_key('own'):
            s['own'] = UserProfile.objects.serialize(ret['own'], template)
        if ret.has_key('connected'):
            s['connected'] = UserProfile.objects.serialize(ret['connected'], template)
        if ret.has_key('follower'):
            s['follower'] = UserProfile.objects.serialize(ret['follower'], template)
        if ret.has_key('follower-d'):
            s['follower-d'] = UserProfile.objects.serialize(ret['follower-d'], template)
        if ret.has_key('followed'):
            s['followed'] = UserProfile.objects.serialize(ret['followed'], template)
        if ret.has_key('others'):
            s['others'] = UserProfile.objects.serialize(ret['others'], template)

        return s

    def split_users(self, me, users):
        own = []
        connected = []
        follower = []
        follower_d = []
        followed = []
        others = []

        ret = dict()

        for user in users:
            connection_status = Wizcard.objects.get_connection_status(me.wizcard, user.wizcard)
            if connection_status is verbs.OWN:
                own.append(user)
            elif connection_status is verbs.CONNECTED:
                # 2-way connected
                connected.append(user)
            elif connection_status is verbs.FOLLOWER:
                follower.append(user)
            elif connection_status is verbs.FOLLOWER_D:
                follower_d.append(user)
            elif connection_status is verbs.FOLLOWED:
                followed.append(user)
            else:
                others.append(user)

        if len(own):
            ret[verbs.OWN] = own
        if len(connected):
            ret[verbs.CONNECTED] = connected
        if len(follower):
            ret[verbs.FOLLOWER] = follower
        if len(follower_d):
            ret[verbs.FOLLOWER_D] = follower_d
        if len(followed):
            ret[verbs.FOLLOWED] = followed
        if len(others):
            ret[verbs.OTHERS] = others

        return ret

    def serialize(self, users, template):
        wizcards = map(lambda u: u.wizcard, users)
        return serialize(wizcards, **template)

    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        userid =  ''.join(random.choice(chars) for x in range(size))
        try:
            User.objects.get(username=userid)
            userid = self.id_generator()
        except ObjectDoesNotExist:
            pass
        return userid

    def gen_password(self, id1, id2, id3=None):
        return id2

    def check_user_exists(self, query_type, query_key):
        if query_type == verbs.INVITE_VERBS[verbs.SMS_INVITE]:
            username = UserProfile.objects.username_from_phone_num(query_key)
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                if user.profile.activated:
                    return user.wizcard
        elif query_type == verbs.INVITE_VERBS[verbs.EMAIL_INVITE]:
            email_wizcards =  Wizcard.objects.filter(email=query_key)
            #AR: Need to change the model to make it uniq
            if email_wizcards:
                return email_wizcards[0]
        return None

    def username_from_phone_num(self, phone_num):
        return phone_num + settings.WIZCARD_USERNAME_EXTENSION

    def futureusername_from_phone_num(self, phone_num):
        return phone_num + settings.WIZCARD_FUTURE_USERNAME_EXTENSION

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User, related_name='profile')
    activated = models.BooleanField(default=False)
    #this is the internal userid
    userid = TruncatingCharField(max_length=100)
    future_user = models.BooleanField(default=False, blank=False)
    location = generic.GenericRelation(LocationMgr)
    do_sync = models.BooleanField(default=False)
    is_profile_private = models.BooleanField(default=False)
    is_wifi_data = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    block_unsolicited = models.BooleanField(default=False)

    IOS = 'ios'
    ANDROID='android'
    DEVICE_CHOICES = (
	(IOS, 'iPhone'),
	(ANDROID, 'Android'),
    )
    device_type = TruncatingCharField(max_length=10,
		    		   choices=DEVICE_CHOICES,
				   default=IOS)
    device_id = TruncatingCharField(max_length=100)
    reg_token = models.CharField(db_index=True,max_length=200)

    objects = UserProfileManager()

    def online_key(self):
        return self.userid

    def online(self):
        cache.set(settings.USER_ONLINE_PREFIX % self.online_key(), timezone.now(),
                settings.USER_LASTSEEN_TIMEOUT)

    def can_send_data(self, on_wifi):
        return True if on_wifi else not self.is_wifi_data

    def last_seen(self):
        now = timezone.now()
        ls = cache.get(settings.USER_ONLINE_PREFIX % self.online_key())
        if bool(ls):
            return(True, (now - ls))
        else:
            return(False, None)

    def is_online(self):
        on, ls = self.last_seen()
        delta = timezone.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)
        if on and (ls < delta):
            return True
        return False

    def is_future(self):
        return self.future_user

    def set_future(self):
        self.activated = False
        self.future_user = True
        self.save()

    def is_ios(self):
        return bool(self.device_type == self.IOS)

    def create_or_update_location(self, lat, lng):
        try:
            l = self.location.get()
            updated = l.do_update(lat, lng)
            l.reset_timer()
            return l
        except ObjectDoesNotExist:
            #create
            l_tuple = location.send(sender=self, lat=lat, lng=lng,
                                    tree="PTREE")
            l_tuple[0][1].start_timer(settings.USER_ACTIVE_TIMEOUT)

    def lookup(self, cache_key, n, count_only=False):
        users = None
        try:
            l = self.location.get()
        except ObjectDoesNotExist:
            return None, None

        result, count = l.lookup(cache_key, n)
        #convert result to query set result
        if count and not count_only:
            users = [UserProfile.objects.get(id=x).user for x in result if UserProfile.objects.filter(id=x, activated=True, is_visible=True).exists()]
        return users, count

    def do_resync(self):
        s = {}
        #add callouts to all serializable objects here

	    #wizcard
        try:
            wizcard = self.user.wizcard
        except ObjectDoesNotExist:
            return s

        s['wizcard'] = wizcard.serialize(fields.wizcard_template_full)
        #flicks (put  before wizconnections since wizconnection could refer to flicks)

        if wizcard.flicked_cards.count():
            wf = wizcard.serialize_wizcardflicks()
            s['wizcard_flicks'] = wf

        #wizconnections
        if wizcard.wizconnections_to.count():
            wc = wizcard.serialize_wizconnections()
            s['wizconnections'] = wc

	# Populate Context for Wizcards that this user  is following
	wizcon_to = wizcard.get_following()
	if wizcon_to:
	    s['context'] = serialize(map(lambda x: x.get_relationship(wizcard).cctx.context, wizcon_to), **fields.cctx_wizcard_template)




        #tables
        tables = VirtualTable.objects.user_tables(self.user)
        if tables.count():
        # serialize created and joined tables
            tbls = VirtualTable.objects.serialize_split(
                    tables,
                    self.user,
                    fields.table_template)
            s['tables'] = tbls

        #dead card
        deadcards = self.user.dead_cards.all()
        if deadcards.count():
            dc = DeadCards.objects.serialize(deadcards)
            s['deadcards'] = dc

        # notifications. This is done by simply setting readed=False for
        # those user.notifs which have acted=False
        # This way, these notifs will be sent natively via get_cards
        Notification.objects.unacted(self.user).update(readed=False)
        return s

class FutureUserManager(models.Manager):
    def check_future_user(self, email=None, phone=None):
        qlist = []
        if email:
            qlist.append(Q(email=email.lower()))
        if phone:
            qlist.append(Q(phone=phone))

        if qlist:
            return self.filter(reduce(operator.or_, qlist))
        return None

class FutureUser(models.Model):
    inviter = models.ForeignKey(User, related_name='invitees')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    phone = TruncatingCharField(max_length=20, blank=True)
    email = EmailField(blank=True)

    objects = FutureUserManager()

    def generate_self_invite(self, real_user):
        cctx = ConnectionContext(
            asset_obj=self.content_object,
            connection_mode=verbs.INVITE_VERBS[verbs.SMS_INVITE] if self.phone
            else verbs.INVITE_VERBS[verbs.EMAIL_INVITE]
        )
        if ContentType.objects.get_for_model(self.content_object) == \
                ContentType.objects.get(model="wizcard"):

            #spoof an exchange, as if it came from the inviter
            rel12 = Wizcard.objects.cardit(self.content_object,
                                           real_user.wizcard,
                                           cctx=cctx)

            #sender always accepts the receivers wizcard
            rel21 = Wizcard.objects.cardit(real_user.wizcard,
                                           self.content_object,
                                           status=verbs.ACCEPTED,
                                           cctx=cctx)
            #Q notif for to_wizcard
            notify.send(self.inviter,
                        recipient=real_user,
                        verb=verbs.WIZREQ_U[0],
                        description=cctx.description,
                        target=self.content_object,
                        action_object=rel12)

            #Q implicit notif for from_wizcard
            notify.send(real_user,
                        recipient=self.inviter,
                        verb=verbs.WIZREQ_T[0],
                        description=cctx.description,
                        target=real_user.wizcard,
                        action_object=rel21)
        elif ContentType.objects.get_for_model(self.content_object) == \
                ContentType.objects.get(model="virtualtable"):
            #Q this to the receiver
            notify.send(self.inviter, recipient=real_user,
                        verb=verbs.WIZCARD_TABLE_INVITE[0],
                        target=self.content_object)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile(user=instance)
        profile.userid = UserProfile.objects.id_generator()
        profile.save()

post_save.connect(create_user_profile, sender=User)
