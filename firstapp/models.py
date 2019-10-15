from django.db import models
import uuid

# Create your models here.
class Submit(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable = False, unique=True)
    url = models.TextField(null=False)
    email = models.TextField(null=True)



class Status(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, unique=True)
    status = models.TextField(null=False)
    hash = models.CharField(max_length=32)