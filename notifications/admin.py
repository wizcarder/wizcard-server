# -*- coding: utf-8 -*-

from django.contrib import admin
from notifications.models import SyncNotification

class NotificationAdmin(admin.ModelAdmin):
    pass

class EmailAndPushAdmin(admin.ModelAdmin):
    pass

admin.site.register(AsyncNotification, EmailAndPushAdmin)
admin.site.register(SyncNotification, NotificationAdmin)
