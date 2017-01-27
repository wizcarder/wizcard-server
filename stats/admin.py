from django.contrib import admin
from stats.models import Stats

# Register your models here.

class StatsAdmin(admin.ModelAdmin):
    list_display = Stats._meta.get_all_field_names()

    pass

admin.site.register(Stats, StatsAdmin)
