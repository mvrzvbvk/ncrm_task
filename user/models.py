from django.db import models
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser


USER_BASIC = 0
USER_MANAGER = 1
USER_TYPE_CHOICES = (
    (USER_BASIC, 'Basic user'),
    (USER_MANAGER, 'Manager user'),
)

class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True, verbose_name='username')
    user_type = models.IntegerField(default=0, choices=USER_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)


    def __str__(self):
        return self.username

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
