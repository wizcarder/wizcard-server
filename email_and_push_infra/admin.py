from django.contrib import admin
from email_and_push_infra.models import EmailAndPush

# Register your models here.

class EmailAndPushAdmin:
    pass

admin.site.register(EmailAndPush, EmailAndPushAdmin)
