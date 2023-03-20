from django.db import models

# Create your models here.
class UsageDate(models.Model):
    usage_date = models.IntegerField()

class BillDate(models.Model):
    user_id = models.IntegerField()
    year = models.IntegerField()
    month = models.IntegerField()

