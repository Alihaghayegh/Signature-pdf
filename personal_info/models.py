from django.db import models
from django.contrib.auth.models import User


class UserInfo(User):
    '''
    Model for taking user info and signature and save it to db
    '''
    signature = models.ImageField(upload_to="signatures")
    time = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return (f"{User.first_name} {User.last_name}")

    class Meta:
        ordering = ['time']
        verbose_name_plural = "User info"


class PDFFile(models.Model):
    '''
    This model is for saving each users own pdf file
    '''
    user = models.OneToOneField(UserInfo, on_delete=models.CASCADE)
    file = models.FileField(upload_to='pdfs/', null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')  # pending, in_progress, done, failed
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"
    

    