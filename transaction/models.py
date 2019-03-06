import string
import random
from django.db import models

# Create your models here.
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings
from django.utils import timezone

from transaction.constants import *
from wallet.models import Wallet


class Transaction(models.Model):
    type = models.CharField(_("Transaction Type"), max_length=10, choices=TRANSACTION_TYPES, default=DEBIT)
    txn_no = models.CharField(_("Transaction Number"), max_length=10)
    # For simple transaction, this field is not required
    # status = models.CharField(_("Status"), max_length=10, choices=STATUSES, default=PENDING)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.FloatField(
        _('Transaction Amount'),
        default=0.0
    )
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if not self.txn_no:
            self.txn_no = self._generate_txn_no()
        super(Transaction, self).save(*args, **kwargs)

    def _generate_txn_no(self):
        """
        Generate a unique transaction number using appropriate prefix.
        """

        prefix = 'TXN-'
        while True:
            txn_no = self._generate_random_string(8, prefix=prefix)
            print("this is the txn_no ===== ", txn_no)
            if not Transaction.objects.filter(txn_no=txn_no).exists():
                return txn_no

    def _generate_random_string(self, size, alphabets_allowed=True, numbers_allowed=True, case_sensitive=False, prefix=''):
        """
        Returns a random string given the size and conditions.
        """

        choices = ""

        if alphabets_allowed:
            choices += string.ascii_uppercase
            if case_sensitive:
                choices += string.ascii_lowercase

        if numbers_allowed:
            choices += string.digits

        return prefix + ''.join(random.choice(choices) for _ in range(size))

    def __str__(self):
        return str(self.txn_no)

    class Meta:
        verbose_name = _("Transaction Order")
        verbose_name_plural = _("Transaction Orders")
        unique_together = ('txn_no', 'wallet')



















#
#
#
#
#
#
# from decimal import Decimal
#
# from django.contrib.contenttypes.fields import GenericForeignKey
# from django.contrib.contenttypes.models import ContentType
# from django.core.validators import validate_comma_separated_integer_list
# from django.db import models
# from django.db.models import Sum
# from django.utils.timezone import now
# from django.utils.translation import ugettext_lazy as _
#
# from cc import settings
# from cc.validator import validate
#
# class Wallet(models.Model):
#     currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
#     balance = models.DecimalField(_('Balance'), max_digits=18, decimal_places=8, default=0)
#     holded = models.DecimalField(_('Holded'), max_digits=18, decimal_places=8, default=0)
#     unconfirmed = models.DecimalField(_('Unconfirmed'), max_digits=18, decimal_places=8, default=0)
#     label = models.CharField(_('Label'), max_length=100, blank=True, null=True, unique=True)
#
#     def __str__(self):
#         return u'{0} {1} "{2}"'.format(self.balance, self.currency.ticker, self.label or '')
#
#     def get_address(self):
#         active = Address.objects.filter(wallet=self, active=True, currency=self.currency)[:1]
#         if active:
#             return active[0]
#
#         unused = Address.objects.filter(wallet=None, active=True, currency=self.currency)[:1]
#         if unused:
#             free = unused[0]
#             free.wallet = self
#             free.save()
#             return free
#
#         old = Address.objects.filter(wallet=self, active=False, currency=self.currency)[:1]
#         if old:
#             return old[0]
#
#
#
#
# class Operation(models.Model):
#     wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
#     created = models.DateTimeField(_('Created'), default=now)
#     balance = models.DecimalField(_('Balance'), max_digits=18, decimal_places=8, default=0)
#     holded = models.DecimalField(_('Holded'), max_digits=18, decimal_places=8, default=0)
#     unconfirmed = models.DecimalField(_('Unconfirmed'), max_digits=18, decimal_places=8, default=0)
#     description = models.CharField(_('Description'), max_length=100, blank=True, null=True)
#     reason_content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
#     reason_object_id = models.PositiveIntegerField(null=True, blank=True)
#     reason = GenericForeignKey('reason_content_type', 'reason_object_id')
#
#
# class Address(models.Model):
#     address = models.CharField(_('Address'), max_length=50, primary_key=True)
#     currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
#     created = models.DateTimeField(_('Created'), default=now)
#     active = models.BooleanField(_('Active'), default=True)
#     label = models.CharField(_('Label'), max_length=50, blank=True, null=True, default=None)
#     wallet = models.ForeignKey(Wallet, blank=True, null=True, related_name="addresses", on_delete=models.CASCADE)
#
#     def __str__(self):
#         return u'{0}, {1}'.format(self.address, self.currency.ticker)
#
#
# class Currency(models.Model):
#     ticker = models.CharField(_('Ticker'), max_length=4, default='BTC', primary_key=True)
#     label = models.CharField(_('Label'), max_length=20, default='Bitcoin', unique=True)
#     magicbyte = models.CharField(_('Magicbytes'), max_length=10, default='0,5', validators=[validate_comma_separated_integer_list])
#     last_block = models.PositiveIntegerField(_('Last block'), blank=True, null=True, default=0)
#     api_url = models.CharField(_('API hostname'), default='http://localhost:8332', max_length=100, blank=True, null=True)
#     dust = models.DecimalField(_('Dust'), max_digits=18, decimal_places=8, default=Decimal('0.0000543'))
#
#     class Meta:
#         verbose_name_plural = _('currencies')
#
#     def __str__(self):
#         return self.label
#
#
# class Transaction(models.Model):
#     txid = models.CharField(_('Txid'), max_length=100)
#     address = models.CharField(_('Address'), max_length=50)
#     currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
#     processed = models.BooleanField(_('Processed'), default=False)
#
#     class Meta:
#         unique_together = (('txid', 'address'),)
#
#
# class WithdrawTransaction(models.Model):
#     NEW = 'NEW'
#     ERROR = 'ERROR'
#     DONE = 'DONE'
#     WTX_STATES = (
#         ('NEW', 'New'),
#         ('ERROR', 'Error'),
#         ('DONE', 'Done'),
#     )
#     currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
#     amount = models.DecimalField(_('Amount'), max_digits=18, decimal_places=8)
#     address = models.CharField(_('Address'), max_length=50)
#     wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
#     created = models.DateTimeField(_('Created'), default=now)
#     txid = models.CharField(_('Txid'), max_length=100, blank=True, null=True, db_index=True)
#     walletconflicts = models.CharField(_('Walletconflicts txid'), max_length=100, blank=True, null=True, db_index=True)
#     state = models.CharField(_('State'), max_length=10, choices=WTX_STATES, default=NEW)
#     fee = models.DecimalField(_('Fee'), max_digits=18, decimal_places=8, null=True, blank=True)
