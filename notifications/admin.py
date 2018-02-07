# -*- coding: utf-8 -*-

from django.contrib import admin
from notifications.models import SyncNotification, AsyncNotification

class SyncNotificationAdmin(admin.ModelAdmin):
    pass

class AsyncNotificationAdmin(admin.ModelAdmin):
    pass

admin.site.register(AsyncNotification, AsyncNotificationAdmin)
admin.site.register(SyncNotification, SyncNotificationAdmin)
