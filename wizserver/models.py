from django.db import models
import pdb

# Create your models here.

#Using this to create proxy model for now. Might put in a separate app if required
from django.contrib.auth.models import User

class MyUser(User):
    class Meta:
        proxy = True

    def clear_default_wizcard_all(self):
        map(lambda a: a.clear_default(), self.wizcards.all())

    def default_wizcard(self):
        q = self.wizcards.all().filter(isDefaultCard=True)
        return q[0]

