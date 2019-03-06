from django.db import models

# Create your models here.
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings
from django.utils import timezone

from users.models import User


class Wallet(models.Model):
    balance = models.FloatField(_("Wallet Balance"), default=0.0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user.national_number)

    class Meta:
        verbose_name = _("Wallet")
        verbose_name_plural = _("Wallets")
