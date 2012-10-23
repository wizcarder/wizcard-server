from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from models import WizConnectionRequest, Wizcard, UserBlocks


class WizConnectionRequestAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ('from_wizcard', 'to_wizcard', 'accepted', 'created')
    list_filter = ('accepted',)
    actions = ('accept_wizconnection', 'decline_wizconnection', 'cancel_wizconnection')

    def accept_wizconnection(self, request, queryset):
        for wizconnection_request in queryset:
            wizconnection_request.accept()
    accept_wizconnection.short_description = _(u'Accept selected wizconnection ' \
                                            u'requests')

    def decline_wizconnection(self, request, queryset):
        for wizconnection_request in queryset:
            wizconnection_request.decline()
    decline_wizconnection.short_description = _(u'Decline selected wizconnection ' \
                                             u'requests')

    def cancel_wizconnection(self, request, queryset):
        for wizconnection_request in queryset:
            wizconnection_request.cancel()
    cancel_wizconnection.short_description = _(u'Cancel selected wizconnection ' \
                                            u'requests')
admin.site.register(WizConnectionRequest, WizConnectionRequestAdmin)


class WizcardAdmin(admin.ModelAdmin):
    list_display = ('user', 'wizconnection_count', 'wizconnection_summary')
admin.site.register(Wizcard, WizcardAdmin)


class UserBlocksAdmin(admin.ModelAdmin):
    list_display = ('user', 'block_count', 'block_summary')
admin.site.register(UserBlocks, UserBlocksAdmin)
