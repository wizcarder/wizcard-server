from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from lib.preserialize.serialize import serialize
from lib import wizlib
from polymorphic.models import PolymorphicModel
from polymorphic.manager import PolymorphicManager
from wizserver import fields, verbs
from location_mgr.models import location, LocationMgr
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from wizcardship.models import WizConnectionRequest, Wizcard
from entity.models import VirtualTable
from entity.models import Campaign, ExhibitorInvitee, Event
from entity.serializers import CampaignSerializer, TableSerializerL1
from wizcardship.serializers import WizcardSerializerL2, DeadCardSerializerL2
from django.core.exceptions import ObjectDoesNotExist
from notifications.signals import notify
from notifications.models import BaseNotification, SyncNotification
from base.cctx import ConnectionContext, NotifContext
from base.char_trunc import TruncatingCharField
from base.emailField import EmailField
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from userprofile.signals import user_type_created
from base_entity.models import UserEntity, BaseEntityComponent
import uuid
import string
import random
import pytz
import datetime
import logging
import operator
import pdb

RECO_DEFAULT_TZ = pytz.timezone(settings.TIME_ZONE)
RECO_DEFAULT_TIME = RECO_DEFAULT_TZ.localize(datetime.datetime(2010, 1, 1))

logger = logging.getLogger(__name__)


class AppUserSettings(models.Model):
    is_profile_private = models.BooleanField(default=False)
    is_wifi_data = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    dnd = models.BooleanField(default=False)
    block_unsolicited = models.BooleanField(default=False)


class WebOrganizerUserSettings(models.Model):
    pass


class WebExhibitorUserSettings(models.Model):
    pass


class UserProfileManager(PolymorphicManager):
    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        userid = ''.join(random.choice(chars) for x in range(size))
        try:
            User.objects.get(username=userid)
            userid = self.id_generator()
        except ObjectDoesNotExist:
            pass
        return userid

    def gen_password(self, id1, id2):
        return id1+id2

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
        admin = UserProfile.objects.filter(is_admin=True)[0].user if \
            UserProfile.objects.filter(is_admin=True).exists() else None
        # should not happen. failsafe just in case
        if not admin:
            admin = User.objects.filter(is_staff=True, is_superuser=True)[0]
            admin.profile.is_admin = True
            admin.profile.save()

        return admin

    def is_admin_user(self, user):
        return user.is_staff and user.is_superuser

    def get_portal_user_internal(self):
        return UserProfile.objects.get(user_type=UserProfile.PORTAL_USER_INTERNAL) \
            if UserProfile.objects.filter(user_type=UserProfile.PORTAL_USER_INTERNAL).exists() else None


class UserProfile(PolymorphicModel):
    # hacking up bitmaps this way
    BITMAP_BASE = 0
    APP_USER = 1
    WEB_ORGANIZER_USER = APP_USER << 1
    WEB_EXHIBITOR_USER = APP_USER << 2
    PORTAL_USER_INTERNAL = APP_USER << 6

    # this is the internal userid
    userid = models.UUIDField(default=uuid.uuid4, editable=False)
    user_type = models.IntegerField(default=BITMAP_BASE)
    user = models.OneToOneField(User, related_name='profile')
    activated = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserProfileManager()

    def app_user(self):
        try:
            return self.baseuser.all().instance_of(AppUser).get()
        except:
            return None

    def organizer_user(self):
        try:
            return self.baseuser.all().instance_of(WebOrganizerUser).get()
        except:
            return None

    def exhibitor_user(self):
        try:
            return self.baseuser.all().instance_of(WebExhibitorUser).get()
        except:
            return None

    def get_baseuser_by_type(self, user_type):
        if user_type & self.APP_USER:
            return self.app_user()
        elif user_type & self.WEB_EXHIBITOR_USER:
            return self.exhibitor_user()
        elif user_type & self.WEB_ORGANIZER_USER:
            return self.organizer_user()
        else:
            raise RuntimeError('%r invalid user type' % (user_type))

    def create_user_type_instance(self, user_type):
        self.user_type |= user_type

        # create the associated user personalities
        if user_type & self.APP_USER:
            if self.app_user():
                raise AssertionError
            user_obj = AppUser.objects.create(
                profile=self,
                settings=AppUserSettings.objects.create()
            )
        elif user_type & self.WEB_ORGANIZER_USER:
            if self.organizer_user():
                raise AssertionError
            user_obj = WebOrganizerUser.objects.create(
                profile=self,
                settings=WebOrganizerUserSettings.objects.create()
            )
        elif user_type & self.WEB_EXHIBITOR_USER:
            if self.exhibitor_user():
                raise AssertionError
            user_obj = WebExhibitorUser.objects.create(
                profile=self,
                settings=WebExhibitorUserSettings.objects.create()
            )
        else:
            raise AssertionError("Invalid user type %s" % user_type)

        self.save()

        # things like future user etc can be done here.
        user_type_created.send(sender=self, user_type=user_type)
        return user_obj

    def is_user_of_type(self, user_type):
        return self.user_type & user_type

    def is_app_user(self):
        return self.is_user_of_type(self.APP_USER)



class BaseUser(PolymorphicModel):
    profile = models.ForeignKey(UserProfile, related_name='%(class)s')

    def connect_subentities(self):
        pass


class AppUser(BaseUser):
    DEVICE_CHOICES = (
        (settings.DEVICE_IOS, 'iPhone'),
        (settings.DEVICE_ANDROID, 'Android'),
    )

    location = GenericRelation(LocationMgr)
    do_sync = models.BooleanField(default=False)
    device_id = TruncatingCharField(max_length=100)
    reg_token = models.CharField(db_index=True, max_length=200)
    device_type = TruncatingCharField(max_length=10, choices=DEVICE_CHOICES)
    reco_generated_at = models.DateTimeField(default=RECO_DEFAULT_TIME)
    reco_ready = models.PositiveIntegerField(default=0)
    settings = models.OneToOneField(AppUserSettings, related_name='base_user')

    objects = UserProfileManager()

    def online_key(self):
        return self.profile.userid

    def online(self):
        cache.set(settings.USER_ONLINE_PREFIX % self.online_key(), timezone.now(),
                  settings.USER_LASTSEEN_TIMEOUT)

    def can_send_data(self, on_wifi):
        return True if on_wifi else not self.is_wifi_data

    def last_seen(self):
        now = timezone.now()
        ls = cache.get(settings.USER_ONLINE_PREFIX % self.online_key())
        if bool(ls):
            return True, (now - ls)
        else:
            return False, None

    def is_online(self):
        on, ls = self.last_seen()
        delta = timezone.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)
        if on and (ls < delta):
            return True
        return False

    def create_or_update_location(self, lat, lng):
        try:
            loc = self.location.get()
            updated = loc.do_update(lat, lng)
            loc.reset_timer()
            return loc
        except ObjectDoesNotExist:
            # create
            l_tuple = location.send(sender=self, lat=lat, lng=lng,
                                    tree="PTREE")
            l_tuple[0][1].start_timer(settings.USER_ACTIVE_TIMEOUT)

    def lookup(self, n, count_only=False):
        users = None
        try:
            loc = self.location.get()
        except ObjectDoesNotExist:
            return None, None

        result, count = loc.lookup(n)
        # convert result to query set result
        if count and not count_only:
            users = [AppUser.objects.get(id=x).profile.user for x in result if
                     AppUser.objects.filter(
                         id=x,
                         profile__activated=True,
                         settings__is_visible=True
                     ).exists()]
            count = len(users)
        return users, count

    def do_resync(self):
        s = {}
        # add callouts to all serializable objects here

        # wizcard
        try:
            wizcard = self.profile.user.wizcard
        except ObjectDoesNotExist:
            return s

        s['wizcard'] = WizcardSerializerL2(wizcard, context={'user': self.profile.user}).data

        # # flicks (put  before wizconnections since wizconnection could refer to flicks)
        # if wizcard.flicked_cards.count():
        #     wf = wizcard.serialize_wizcardflicks()
        #     s['wizcard_flicks'] = wf

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

            s['context'] = serialize(cctx)

        # tables
        tables = VirtualTable.objects.users_entities(
            self.profile.user,
            user_filter={'state': UserEntity.JOIN},
            entity_filter={'entity_state': BaseEntityComponent.ENTITY_STATE_PUBLISHED}
        )

        if tables:
            # serialize created and joined tables
            tbls = TableSerializerL1(tables, many=True, context={'user': self.profile.user}).data
            s['tables'] = tbls

        # dead card
        deadcards = self.profile.user.dead_cards.filter(activated=True)
        if deadcards.count():
            dc = DeadCardSerializerL2(deadcards, many=True, context={'user': self.profile.user}).data
            s['deadcards'] = dc

        campaigns = Campaign.objects.users_entities(
            self.profile.user,
            user_filter={'state': UserEntity.PIN},
            entity_filter={'entity_state': BaseEntityComponent.ENTITY_STATE_PUBLISHED}
        )

        if campaigns:
            camp_data = CampaignSerializer(campaigns, many=True, context={'user': self.profile.user}).data
            s['campaigns'] = camp_data

        # events. Using L1 serializer. App will call detail on these events when needed.

        events = Event.objects.users_entities(
            self.profile.user,
            user_filter={'state__in': [UserEntity.JOIN, UserEntity.PIN]}
        )

        if len(events):
            _ser = BaseEntityComponent.entity_ser_from_type_and_level(
                entity_type=BaseEntityComponent.EVENT,
                level=BaseEntityComponent.SERIALIZER_L0
            )
            evts = _ser(events, many=True, context={'user': self.profile.user}).data
            s['events'] = evts

        # notifications. This is done by simply setting readed=False for
        # those user.notifs which have acted=False
        # This way, these notifs will be sent natively via get_cards
        SyncNotification.objects.unacted(self.profile.user).update(readed=False)
        return s


class WebOrganizerUser(BaseUser):
    settings = models.OneToOneField(WebOrganizerUserSettings, related_name='base_user')


class WebExhibitorUser(BaseUser):
    settings = models.OneToOneField(WebExhibitorUserSettings, related_name='base_user')

    def connect_subentities(self):
        # any pending invite ?
        invite_objs = ExhibitorInvitee.objects.check_pending_invites(email=self.profile.user.email)

        # each of these invites were related with event when the invite was sent by organizer
        invited_events = [item for sublist in invite_objs for item in sublist.get_parent_entities_by_contenttype_id(ContentType.objects.get(model="event"))]

        # join this User to the Event. We can retrieve this users Events on the portal. Additionally, we need to be
        # aware (and potentially filter out) that "joined users" also contain Exhibitor Users.
        user = self.profile.user
        [event.user_attach(user, state=UserEntity.JOIN) for event in invited_events]
        invite_objs.update(state=ExhibitorInvitee.ACCEPTED)


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
    content_object = GenericForeignKey('content_type', 'object_id')
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
            notify.send(
                self.inviter,
                recipient=real_user,
                notif_tuple=verbs.WIZREQ_U,
                description=cctx.description,
                target=self.content_object,
                action_object=rel12
            )

            # Q implicit notif for from_wizcard
            notify.send(
                real_user,
                recipient=self.inviter,
                notif_tuple=verbs.WIZREQ_T,
                description=cctx.description,
                target=real_user.wizcard,
                action_object=rel21
            )
        elif ContentType.objects.get_for_model(self.content_object) == \
                ContentType.objects.get(model="virtualtable"):
            # Q this to the receiver
            notify.send(
                self.inviter, recipient=real_user,
                notif_tuple=verbs.WIZCARD_TABLE_INVITE,
                target=self.content_object
            )


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
        return self.first_name + " " + self.last_name + " " + self.email + " " + self.phone

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
        profile.save()


post_save.connect(create_user_profile, sender=User, dispatch_uid="users-profilecreation-signal")
