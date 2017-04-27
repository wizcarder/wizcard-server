from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from lib.preserialize.serialize import serialize
from lib import wizlib
from wizserver import fields, verbs
from location_mgr.models import location, LocationMgr
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from wizcardship.models import WizConnectionRequest, Wizcard
from entity.models import VirtualTable
from dead_cards.models import DeadCards
from django.core.exceptions import ObjectDoesNotExist
from notifications.models import notify
from notifications.models import Notification
from base.cctx import ConnectionContext, NotifContext
from base.char_trunc import TruncatingCharField
from base.emailField import EmailField
import operator
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
import string
import random
import pytz
import datetime
import logging
import pdb

RECO_DEFAULT_TZ = pytz.timezone(settings.TIME_ZONE)
RECO_DEFAULT_TIME = RECO_DEFAULT_TZ.localize(datetime.datetime(2010,01,01))

logger = logging.getLogger(__name__)

# hacking up bitmaps this way
BITMAP_BASE = 1
WIZCARD_USER = BITMAP_BASE
WIZWEB_USER = BITMAP_BASE << 1
WIZWEB_ADMIN = BITMAP_BASE << 2
WIZEVENT_USER = BITMAP_BASE << 3
WIZPRODUCT_USER = BITMAP_BASE << 4
WIZBUSINESS_USER = BITMAP_BASE << 5
PORTAL_USER_INTERNAL = BITMAP_BASE << 6

class UserProfileManager(models.Manager):

    def serialize_split(self, me, users):
        s = dict()
        template = fields.wizcard_template_brief

        ret = self.split_users(me, users)
        if ret.has_key('own'):
            s['own'] = UserProfile.objects.serialize(ret['own'], template)
        if ret.has_key('connected'):
            s['connected'] = UserProfile.objects.serialize(ret['connected'], template)
        # lets remove follower for now. The *assumption* is that follower is represented on
        # the me.app as a notif anyway. Since they are on the same screen, it's redundant.
        # if ret.has_key('follower'):
        #    s['follower'] = UserProfile.objects.serialize(ret['follower'], template)
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
            if connection_status == verbs.OWN:
                own.append(user)
            elif connection_status == verbs.CONNECTED:
                # 2-way connected
                connected.append(user)
            elif connection_status == verbs.FOLLOWER:
                follower.append(user)
            elif connection_status == verbs.FOLLOWER_D:
                follower_d.append(user)
            elif connection_status == verbs.FOLLOWED:
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
        userid = ''.join(random.choice(chars) for x in range(size))
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
            email_wizcards = Wizcard.objects.filter(email=query_key)
            # AR: Need to change the model to make it uniq
            if email_wizcards:
                return email_wizcards[0]
        return None

    def username_from_phone_num(self, phone_num):
        return phone_num + settings.WIZCARD_USERNAME_EXTENSION

    def futureusername_from_phone_num(self, phone_num):
        return phone_num + settings.WIZCARD_FUTURE_USERNAME_EXTENSION

    def get_admin_user(self):
        return User.objects.filter(is_staff=True, is_superuser=True)[0] \
            if User.objects.filter(is_staff=True, is_superuser=True).exists() else None

    def is_admin_user(self, user):
        return user.is_staff and user.is_superuser

    def get_portal_user_internal(self):
        return UserProfile.objects.get(user_type=PORTAL_USER_INTERNAL) \
            if UserProfile.objects.filter(user_type=PORTAL_USER_INTERNAL).exists() else None

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User, related_name='profile')
    is_admin = models.BooleanField(default=False)
    activated = models.BooleanField(default=False)
    # this is the internal userid
    userid = TruncatingCharField(max_length=100)
    future_user = models.BooleanField(default=False, blank=False)
    location = generic.GenericRelation(LocationMgr)
    do_sync = models.BooleanField(default=False)
    is_profile_private = models.BooleanField(default=False)
    is_wifi_data = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    dnd = models.BooleanField(default=False)
    block_unsolicited = models.BooleanField(default=False)
    reco_generated_at = models.DateTimeField(default=RECO_DEFAULT_TIME)
    reco_ready = models.PositiveIntegerField(default=0)

    IOS = 'ios'
    ANDROID = 'android'
    BROWSER = 'Browser'
    DEVICE_CHOICES = (
        (IOS, 'iPhone'),
        (ANDROID, 'Android'),
        (BROWSER, 'Browser')
    )

    user_type = models.IntegerField(default=WIZCARD_USER)

    device_type = TruncatingCharField(max_length=10,
                                      choices=DEVICE_CHOICES,
                                      default=IOS)

    device_id = TruncatingCharField(max_length=100)
    reg_token = models.CharField(db_index=True, max_length=200)

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
            return (True, (now - ls))
        else:
            return (False, None)

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

    def set_user_type(self, type):
        self.type = type
        self.save()

    def add_user_type(self, type):
        self.type = self.type & type
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
            # create
            l_tuple = location.send(sender=self, lat=lat, lng=lng,
                                    tree="PTREE")
            l_tuple[0][1].start_timer(settings.USER_ACTIVE_TIMEOUT)

    def lookup(self, n, count_only=False):
        users = None
        try:
            l = self.location.get()
        except ObjectDoesNotExist:
            return None, None

        result, count = l.lookup(n)
        # convert result to query set result
        if count and not count_only:
            users = [UserProfile.objects.get(id=x).user for x in result if
                     UserProfile.objects.filter(id=x, activated=True, is_visible=True).exists()]
            count = len(users)
        return users, count

    def do_resync(self):
        s = {}
        # add callouts to all serializable objects here

        # wizcard
        try:
            wizcard = self.user.wizcard
        except ObjectDoesNotExist:
            return s

        s['wizcard'] = wizcard.serialize(fields.wizcard_template_full)
        # flicks (put  before wizconnections since wizconnection could refer to flicks)

        if wizcard.flicked_cards.count():
            wf = wizcard.serialize_wizcardflicks()
            s['wizcard_flicks'] = wf

        # wizconnections
        if wizcard.wizconnections_from.count():
            wc = wizcard.serialize_wizconnections()
            s['wizconnections'] = wc

        # Populate Context for Wizcards that this user  is following
        conn = WizConnectionRequest.objects.filter(to_wizcard=wizcard, status=verbs.ACCEPTED)
        if conn:
            cctx = map(lambda x: NotifContext(
                description=x.cctx.description,
                asset_id=x.cctx.asset_id,
                asset_type=x.cctx.asset_type,
                connection_mode=x.cctx.connection_mode,
                notes=x.cctx.notes,
                timestamp=x.created.strftime("%d %B %Y")).context, conn)

            s['context'] = serialize(cctx, **fields.cctx_wizcard_template)

        # tables
        tables = VirtualTable.objects.users_entities(self.user)
        if tables.count():
            # serialize created and joined tables
            tbls = VirtualTable.objects.serialize_split(
                tables,
                self.user,
                fields.table_template)
            s['tables'] = tbls

        # dead card
        deadcards = self.user.dead_cards.filter(activated=True)
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
    created = models.DateTimeField(auto_now_add=True)

    objects = FutureUserManager()

    def generate_self_invite(self, real_user):
        cctx = ConnectionContext(
            asset_obj=self.content_object,
            connection_mode=verbs.INVITE_VERBS[verbs.SMS_INVITE] if self.phone
            else verbs.INVITE_VERBS[verbs.EMAIL_INVITE]
        )
        if ContentType.objects.get_for_model(self.content_object) == \
                ContentType.objects.get(model="wizcard"):

            # spoof an exchange, as if it came from the inviter
            rel12 = Wizcard.objects.cardit(self.content_object,
                                           real_user.wizcard,
                                           cctx=cctx)
            cctx = ConnectionContext(
                asset_obj=real_user.wizcard,
                connection_mode=verbs.INVITE_VERBS[verbs.SMS_INVITE] if self.phone
                else verbs.INVITE_VERBS[verbs.EMAIL_INVITE]
            )
            # sender always accepts the receivers wizcard
            rel21 = Wizcard.objects.cardit(real_user.wizcard,
                                           self.content_object,
                                           status=verbs.ACCEPTED,
                                           cctx=cctx)
            # Q notif for to_wizcard
            notify.send(self.inviter,
                        recipient=real_user,
                        verb=verbs.WIZREQ_U[0],
                        description=cctx.description,
                        target=self.content_object,
                        action_object=rel12)

            # Q implicit notif for from_wizcard
            notify.send(real_user,
                        recipient=self.inviter,
                        verb=verbs.WIZREQ_T[0],
                        description=cctx.description,
                        target=real_user.wizcard,
                        action_object=rel21)
        elif ContentType.objects.get_for_model(self.content_object) == \
                ContentType.objects.get(model="virtualtable"):
            # Q this to the receiver
            notify.send(self.inviter, recipient=real_user,
                        verb=verbs.WIZCARD_TABLE_INVITE[0],
                        target=self.content_object)


# Model for Address-Book Support. Standard M2M-through
MIN_MATCHES_FOR_PHONE_DECISION = 3
MIN_MATCHES_FOR_EMAIL_DECISION = 3
MIN_MATCHES_FOR_NAME_DECISION = 4


class AddressBook(models.Model):
    # this is the high confidence, cleaned up phone
    phone = TruncatingCharField(max_length=20, blank=True)
    # to indicate if above entry is definitely the right one
    phone_finalized = models.BooleanField(default=False)

    email = EmailField(blank=True)
    # to indicate if above entry is definitely the right one
    email_finalized = models.BooleanField(default=False)

    first_name = TruncatingCharField(max_length=40, blank=True)
    last_name = TruncatingCharField(max_length=40, blank=True)
    # to indicate if above entry is definitely the right one
    first_name_finalized = models.BooleanField(default=False)
    last_name_finalized = models.BooleanField(default=False)
    users = models.ManyToManyField(User, through='AB_User')

    def __repr__(self):
        return self.first_name + " " + self.last_name + " " + (self.email) + " " + self.phone

    def serialize(self, template=fields.addressbook_template):
        return serialize(self, **template)

    # look through all the candidates and check if there is
    # a majority wins case
    def run_finalize_decision(self):
        save = False
        try:
            if not self.phone_finalized and self.candidate_phones.count():
                common, count = wizlib.most_common(map(lambda x: x.phone, self.candidate_phones.all()))
                if count >= MIN_MATCHES_FOR_PHONE_DECISION:
                    self.phone = common
                    self.phone_finalized = True
                    save = True

            if not self.email_finalized and self.candidate_emails.count():
                common, count = wizlib.most_common(map(lambda x: x.email, self.candidate_emails.all()))
                if count >= MIN_MATCHES_FOR_EMAIL_DECISION:
                    self.email = common
                    self.email_finalized = True
                    save = True

            if not self.first_name_finalized and self.candidate_names.count():
                common, count = wizlib.most_common(map(lambda x: x.first_name, self.candidate_names.all()))
                if count >= MIN_MATCHES_FOR_NAME_DECISION:
                    self.first_name = common
                    self.first_name_finalized = True
                    save = True

            if not self.last_name_finalized and self.candidate_names.count():
                common, count = wizlib.most_common(map(lambda x: x.last_name, self.candidate_names.all()))
                if count >= MIN_MATCHES_FOR_NAME_DECISION:
                    self.last_name = common
                    self.last_name_finalized = True
                    save = True
            if save:
                self.save()
        except:
            # really weird..adding debugs to see wtf is happening
            logger.error('WTF IS HAPPENING %s: %s, %s, %s',
                         self,
                         self.candidate_names.all(),
                         self.candidate_phones.all(),
                         self.candidate_emails.all())
            pass

    def get_phone(self):
        if self.phone_finalized:
            return self.phone
        else:
            if self.candidate_phones.all():
                return wizlib.most_common(map(lambda x: x.phone, self.candidate_phones.all()))[0]
            else:
                return ""

    def get_all_phones(self):
        if self.phone_finalized:
            return [self.phone]
        else:
            if self.candidate_phones.all():
                return [wizlib.most_common(map(lambda x: x.phone, self.candidate_phones.all()))[0]]
            else:
                return []

    def get_all_emails(self):
        if self.email_finalized:
            return [self.email]
        else:
            if self.candidate_emails.all():
                return [wizlib.most_common(map(lambda x: x.email, self.candidate_emails.all()))[0]]
            else:
                return []

    def get_email(self):
        if self.email_finalized:
            return self.email
        else:
            if self.candidate_emails.all():
                return wizlib.most_common(map(lambda x: x.email, self.candidate_emails.all()))[0]
            else:
                return ""

    def get_name(self):
        first_name = \
            self.first_name if self.first_name_finalized else \
                wizlib.most_common(map(lambda x: x.first_name, self.candidate_names.all()))[0]
        last_name = self.last_name if self.last_name_finalized else \
            wizlib.most_common(map(lambda x: x.last_name, self.candidate_names.all()))[0]

        return first_name.capitalize() + " " + last_name.capitalize()

    def is_phone_final(self):
        return self.phone_finalized

    def is_email_final(self):
        return self.email_finalized

    def is_name_final(self):
        return self.first_name_finalized and self.last_name_finalized


class AB_Candidate_Phones(models.Model):
    phone = TruncatingCharField(max_length=20)
    ab_entry = models.ForeignKey(AddressBook, related_name='candidate_phones')

    def __repr__(self):
        return self.phone


class AB_Candidate_Emails(models.Model):
    email = EmailField()
    ab_entry = models.ForeignKey(AddressBook, related_name='candidate_emails')

    def __repr__(self):
        return self.email


class AB_Candidate_Names(models.Model):
    first_name = TruncatingCharField(max_length=40)
    last_name = TruncatingCharField(max_length=40)
    ab_entry = models.ForeignKey(AddressBook, related_name='candidate_names')

    def __repr__(self):
        return self.first_name + " " + self.last_name


class AB_User(models.Model):
    user = models.ForeignKey(User)
    ab_entry = models.ForeignKey(AddressBook)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile(user=instance)
        if UserProfile.objects.is_admin_user(instance):
            profile.is_admin = True
        profile.userid = UserProfile.objects.id_generator()
        profile.save()


post_save.connect(create_user_profile, sender=User)
