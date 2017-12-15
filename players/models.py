# noinspection PyUnresolvedReferences
from django.db import models


class Player(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=50)
    fullname = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name
