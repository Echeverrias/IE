from django.db import models

# Create your models here.

class Chart(models.Model):
    x = models.IntegerField(default=15)
    y = models.IntegerField(default=25)
