from django.db import models

# Create your models here.

from base.mixins import Base411Mixin, Base412Mixin, CompanyTitleMixin
from base_entity.models import BaseEntityComponent, BaseEntityComponentManager


class ScannedEntityManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.SCANNED_USER):
        return super(ScannedEntityManager, self).owners_entities(
            user,
            entity_type=entity_type
        )


class ScannedEntity(BaseEntityComponent, Base411Mixin, CompanyTitleMixin):

    # we will encode event_id in the QR code. This allows us to map the scan
    # to the event and thus to the campaign at the event (scanner user would
    # first have to have been added as owner to the campaign on the exhibitor
    # portal
    event_id = models.PositiveIntegerField(blank=True, null=True)

    objects = ScannedEntityManager()

    def lead_score(self):
        return 10

    # no notifs required for this one
    def post_connect_remove(self, parent, **kwargs):
        kwargs.update(send_notif=False)
        return super(ScannedEntity, self).post_connect_remove(parent, **kwargs)


class BadgeTemplateManager(BaseEntityComponentManager):
    def owners_entities(self, user, entity_type=BaseEntityComponent.BADGE_TEMPLATE):
        return super(BadgeTemplateManager, self).owners_entities(
            user,
            entity_type=entity_type
        )

# Portal can use this if required to hold any data for the template.
# The data will simple be an opaque set of values. Server will not
# interpret anything. It'll simply hold and retrieve it. ext_fields
# inherited will contain all of this.
# website can be used as is.
# description can be used as the portal needs based on the UI fields


class BadgeTemplate(BaseEntityComponent, Base412Mixin, CompanyTitleMixin):

    objects = BadgeTemplateManager()

    # no notifs required for this one
    def post_connect_remove(self, parent, **kwargs):
        kwargs.update(send_notif=False)
        return super(BadgeTemplate, self).post_connect_remove(parent, **kwargs)
