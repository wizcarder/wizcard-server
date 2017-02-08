from django.contrib import admin
from models import EmailAndPush

# Register your models here.

class EmailAndPushAdmin(admin.ModelAdmin):
    pass

admin.site.register(EmailAndPush, EmailAndPushAdmin)
