import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

logging.basicConfig(level=logging.DEBUG)


class UserManager(BaseUserManager):
    """
    Custom manager for user
    """

    def _create_user(self, email, password, is_superuser, **extra_fields):
        """
        Create and Save an User with email and password
            :param str email: user email
            :param str password: user password
            :param bool is_superuser: whether user admin or not
            :return users.models.User user: user
            :raise ValueError: email is not set
        """
        now = timezone.now()

        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)

        is_active = extra_fields.pop("is_active", False)

        user = self.model(email=email, is_active=is_active,
                          is_superuser=is_superuser, last_login=now,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save an User with email and password
        :param str email: user email
        :param str password: user password
        :return users.models.User user: regular user
        """
        return self._create_user(email, password, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save an User with the given email and password.
        :param str email: user email
        :param str password: user password
        :return users.models.User user: admin user
        """
        return self._create_user(email, password, True, True, is_active=True,
                                 **extra_fields)

    def do_login(self, request, email=None,
                 password=None, user=None, **extra_fields):
        """
            Returns the JWT token in case of success, returns the error response in case of login failed.
        """
        if user:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
        else:
            if not email:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='Email is mandatory.')

            user = authenticate(email=email, password=password)

        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data='Incorrect email or password')

        # Return if the user is not active.
        if not user.is_active:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data='Account activation pending')

        # Login the User
        login(request, user)
        token = self.generate_auth_token(user)

        response = {
            'token': token,
            'user': user
        }
        return Response(status=status.HTTP_200_OK, data=response)

    def _set_response(self, is_success, _status, message):
        return {
            'is_success': is_success,
            'status': _status,
            'message': message
        }

    def generate_auth_token(self, user):
        # Generating the JWT Token
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return token


class User(AbstractBaseUser, PermissionsMixin):
    """
    Here email is being used as USERNAME_FIELD for authentication
    The following attributes are inherited from the superclasses:
        * password
        * last_login
        * is_superuser
    """
    name = models.CharField(
        _('Name of User'), blank=True, max_length=255, db_index=True)

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        db_index=True
    )

    is_active = models.BooleanField(_('active'), default=False, help_text=_(
        'Designates whether this user should be treated as '
        'active. Unselect this instead of deleting accounts.'))

    phone = PhoneNumberField(
        _("Mobile Number"), blank=True,
        unique=True,
        help_text=_("Primary mobile number e.g. +91{10 digit mobile number}"))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    @property
    def national_number(self):
        if self.phone:
            return self.phone.national_number
        return '%s' % self.phone
