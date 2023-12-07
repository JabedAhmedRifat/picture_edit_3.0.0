from django.db import models
from django.contrib.auth.models import User
from knox.models import AuthToken

class APIKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    auth_token = models.OneToOneField(AuthToken, on_delete=models.CASCADE)
    key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)