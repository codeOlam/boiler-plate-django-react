from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin)

# Create your models here.


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Must provide a valide email address")
        if not password:
            raise ValueError("Must provide password for your account")

        now = timezone.now()
        user = self.model(
            email=self.normalize_email(email),
            created_at=now,
            last_login=now,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        if email is None:
            raise ValueError("email can not be empty!")

        if password is None:
            raise ValueError("Password can not be empty!")

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True, blank=True)
    email = models.EmailField(
        max_length=127,
        unique=True,
        null=False,
        blank=False)
    username = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        help_text='a nickname',
        blank=True,
        null=True)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    created_at = models.DateTimeField(
        'Date Joined',
        auto_now_add=True,
        null=True)
    updeted_at = models.DateTimeField('Date Updated', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    # you can always defined your user attr below as a django model class
    is_usertype_a = models.BooleanField(default=False)
    is_usertype_b = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        app_label = "accounts"
        db_table = "users"
        verbose_name = "Users Account"
        verbose_name_plural = "Users Account"

    def __str__(self):
        return self.email

    def tokens(self):
        return ""

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
