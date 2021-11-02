from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin)

# Create your models here.


class UserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Must provide a valide email address")

        now = timezone.now()
        user = self.model(
            email=self.normalize_email(email),
            date_joined=now,
            last_login=now,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.model(email, **extra_fields)
        user.set_password(password)
        user.is_admin = True,
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self.db)

        return user
