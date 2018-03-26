from django.db import models


class Record(models.Model):
    id1 = models.CharField(max_length=200)
    id2 = models.CharField(max_length=200)
    action1 = models.IntegerField()
    action2 = models.IntegerField()
    competition_id = models.CharField(max_length=400)

    count = models.IntegerField()
    date = models.DateTimeField()

    def action(self, id):
        if self.id1 == id:
            return self.action1
        else:
            assert self.id2 == id
            return self.action2
