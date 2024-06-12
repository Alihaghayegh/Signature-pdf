from django.db import models
from django.contrib.auth.models import User


class UserInfo(User):
    '''
    Model for taking user info and signature and save it to db
    '''
    signature = models.ImageField(upload_to="signatures")
    credentials = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_credentials")
    time = models.DateTimeField()
    

    def __str__(self):
        return (f"{User.first_name} {User.last_name}")

    class Meta:
        ordering = ['time']
        verbose_name_plural = "User info"
