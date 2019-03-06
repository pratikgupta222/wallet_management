import string
import random
from django.db import models

# Create your models here.
from django.utils.translation import ugettext_lazy as _
from django.db import models

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
            if not Transaction.objects.filter(txn_no=txn_no).exists():
                return txn_no

    def _generate_random_string(self, size, alphabets_allowed=True, numbers_allowed=True, case_sensitive=False,
                                prefix=''):
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
