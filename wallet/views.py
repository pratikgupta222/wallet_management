from django.shortcuts import render

# System and Django libraries
import os
import json
import logging
import traceback
import phonenumbers
from django.db import transaction
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# 3rd Party libraries
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.permissions import CsrfExemptSessionAuthentication
from transaction import constants as txn_const
from transaction.serializers import TransactionListSerializer
from wallet.serializers import WalletSerializer
from wallet import helpers as wall_helper
from transaction.models import Transaction
from wallet.models import Wallet

# Create your views here.
class WalletTransaction(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data

        user = request.user

        validated_data = wall_helper.validate_wallet_transaction_data(data, user)

        if not (validated_data.get(
            'ret_status', status.HTTP_400_BAD_REQUEST) == status.HTTP_200_OK):
            return Response(status=validated_data.pop('ret_status'),
                            data=validated_data)

        with transaction.atomic():
            wallet = validated_data.pop('wallet')
            txn_data = {
                "type": data["txn_type"],
                "wallet": wallet,
                "amount": data["amount"]
            }

            try:
                txn = Transaction.objects.create(**txn_data)
            except Exception as e:
                logging.info(e)
                transaction.set_rollback(True)
                return Response(
                    e.args[0], status=status.HTTP_400_BAD_REQUEST
                )

            wallet_serializer = WalletSerializer(instance=wallet,
                data={"balance":validated_data.get('balance')}, partial=True)

            if wallet_serializer.is_valid():
                wallet_serializer.save()
            else:
                logging.info(wallet_serializer.errors)
                transaction.set_rollback(True)
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data=wallet_serializer.errors)

        response = {
            "status": "PASS",
            "transaction_no": str(txn),
            "message": validated_data.get('message'),
            "balance": validated_data.get('balance')
        }

        return Response(status=status.HTTP_200_OK, data=response)


class WalletBalance(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        try:
            wallet = Wallet.objects.get(user=user)
        except ObjectDoesNotExist:
            response = {
                'status': 'FAIL',
                'message': 'No wallet found for you'
            }

            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=response)

        response = {
            'status': 'PASS',
            'balance': wallet.balance
        }

        return Response(status=status.HTTP_200_OK, data=response)

class WalletHistory(views.APIView):
    permission_classes = (IsAuthenticated,)

    def __get_pagination_data(self, queryset, page, num):
        paginator = Paginator(queryset, num)
        try:
            objects = paginator.page(page)
        except PageNotAnInteger:
            objects = paginator.page(1)
        except EmptyPage:
            objects = paginator.page(paginator.num_pages)
        count = paginator.count

        previous = (
            None if not objects.has_previous() else objects.previous_page_number()
        )
        next = 0 if not objects.has_next() else objects.next_page_number()

        # pages_count = paginator.num_pages
        data = {
            "count": count,
            "previous": previous,
            "next": next,
            "objects": objects.object_list,
        }

        return data

    def get_queryset(self, query_params, user):
        filter_data = {}
        logging.info(
            "Following is the query params for the driver list :"
            " " + str(query_params)
        )

        page_to_be_displayed = (
            query_params.get("next")
            if query_params.get("next", "") and int(query_params["next"]) > 0
            else txn_const.PAGE_TO_BE_DISPLAYED
        )
        logging.info(
            "Page to be displayed for the pagination "
            "purpose: % s" % page_to_be_displayed
        )

        number_of_entry = txn_const.NUMBER_OF_ENTRY_IN_PAGE
        logging.info(
            "Number of entry per page for pagination " "purpose: %s" % number_of_entry
        )

        filter_data["wallet__user"] = user

        # For now considering all the transactions have to be displayed.
        # Later we can take the parameters for filtering of data

        transaction_qs = Transaction.objects.filter(
            **filter_data).order_by("id")

        pagination_data = self.__get_pagination_data(
            transaction_qs, page_to_be_displayed, number_of_entry
        )

        transaction_qs = pagination_data.pop("objects")

        transaction_qs = transaction_qs.select_related("wallet", "wallet__user")

        transaction_history = TransactionListSerializer(transaction_qs, many=True)

        return {"transaction_history": transaction_history.data, "pagination_data": pagination_data}

    def get(self, request):
        user = request.user

        logging.info(
            "Following is the request data for fetching driver list : %s"
            % str(request.GET)
        )

        query_params = request.GET.dict()

        queryset_data = self.get_queryset(query_params, user)
        transaction_history = queryset_data.get("transaction_history")

        data = queryset_data.get("pagination_data")

        if transaction_history:
            return Response(status=status.HTTP_200_OK, data=queryset_data)

        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data="No transaction found")
