from django.db import models


class Record(models.Model):
    user_id = models.CharField(max_length=200)
    competitor_id = models.CharField(max_length=200)
    user_action = models.IntegerField()
    competitor_action = models.IntegerField()
    count = models.IntegerField()
    date = models.DateTimeField()
