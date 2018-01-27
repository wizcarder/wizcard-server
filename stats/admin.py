from django.contrib import admin
from stats.models import Stats
from itertools import chain

# Register your models here.

class StatsAdmin(admin.ModelAdmin):
    list_display = list(set(chain.from_iterable(
        (field.name, field.attname) if hasattr(field, 'attname') else (field.name,)
        for field in Stats._meta.get_fields()
    # For complete backwards compatibility, you may want to exclude
    # GenericForeignKey from the results.
        if not (field.many_to_one and field.related_model is None)
)))

admin.site.register(Stats, StatsAdmin)
