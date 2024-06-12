from django.db import models
from django.contrib.auth.models import User


class UserInfo(User):
    '''
    Model for taking user info and signature and save it to db
    '''
    first_name = models.TextField(max_length=250, blank=False)
    last_name = models.TextField(max_length=250, blank=False)
    signature = models.ImageField(upload_to="signatures")
    credentials = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_credentials")
    time = models.DateTimeField()
    

    def __str__(self):
        return (f"{self.first_name} {self.last_name}")

    class Meta:
        ordering = ['time']
        verbose_name_plural = "User info"
