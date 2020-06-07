from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_staff=False, is_active=True, is_admin=False):
        if not email:
            raise ValueError("User must have an email address")

        if not password:
            raise ValueError("User must have an password")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.staff = is_staff
        user.admin = is_admin
        # user.is_superuser = is_superuser
        user.active = is_active
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password=None):
        user = self.create_user(email, password=password, is_staff=True)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password=password, is_staff=True, is_admin=True)
        user.is_superuser = True
        user.save(using=self._db)
        # user.is_superuser = True
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Database model for users in thr system"""
    first_name = models.CharField('First Name', max_length=20, null=True, blank=True)
    last_name = models.CharField('Last Name', max_length=20, null=True, blank=True)
    email = models.EmailField('Email ID', max_length=255, unique=True)
    contact = models.CharField('Contact Number', max_length=10, null=True, blank=True)
    city = models.CharField('City', max_length=100, null=True, blank=True)
    DOB = models.DateField('Date of Birth', null=True, blank=True)
    timestamp = models.DateTimeField('Registered Date', auto_now_add=True)
    password = models.CharField(max_length=255)
    active = models.BooleanField('Active User', default=False)
    staff = models.BooleanField('Staff User', default=False)
    admin = models.BooleanField('Superuser', default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_active(self):
        return self.active

    @property
    def is_admin(self):
        return self.admin


class Information(models.Model):
    auth_id = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='id', on_delete=models.CASCADE, verbose_name=u'User')
    info = models.TextField(verbose_name='Information')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'timestamp'
