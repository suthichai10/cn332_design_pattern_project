from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class User_profile(models.Model) :

    ezpdf_user = models.OneToOneField(User , on_delete = models.CASCADE)
    folder_id = models.CharField(max_length=44)
