import logging
from rest_framework import status
from wallet.models import Wallet
from wallet.serializers import WalletSerializer
from transaction.constants import CREDIT, DEBIT

def create_wallet_for_user(user):
    response = {
        'ret_status': status.HTTP_400_BAD_REQUEST,
        'message': ''
    }
    if not user:
        response['message'] = 'No user found'
        return response

    wallet_creation_data = {
        'balance': 0,
        'user': user.id
    }

    wallet_serializer = WalletSerializer(data=wallet_creation_data)

    if wallet_serializer.is_valid():
        wallet_serializer.save()
    else:
        logging.info(wallet_serializer.errors)
        response['message'] = wallet_serializer.errors
        return response

    response['ret_status'] = status.HTTP_201_CREATED
    response['message'] = 'Walled Created'

    return response

def validate_wallet_transaction_data(data, user):
    response = {}

    if not data.get("txn_type", None) in [CREDIT, DEBIT]:
        response = {
            'status': 'FAIL',
            'ret_status': status.HTTP_400_BAD_REQUEST,
            'message': 'Please enter valid transaction type'
        }

        return response

    try:
        amount = float(data.get("amount", None))
        if amount <= 0:
            raise ValueError()
    except ValueError:
        response = {
            'status': 'FAIL',
            'ret_status': status.HTTP_400_BAD_REQUEST,
            'message': 'Please enter amount greater than 0'
        }

        return response

    try:
        wallet = Wallet.objects.get(user=user)
    except ObjectDoesNotExist:
        response = {
            'status': 'FAIL',
            'ret_status': status.HTTP_400_BAD_REQUEST,
            'message': 'Please Signup to get your personal wallet'
        }

        return response

    wallet_amount = wallet.balance

    if data["txn_type"] == CREDIT:
        wallet_amount += amount
        response['message'] = 'Amount credited successfully'
    else:
        wallet_amount -= amount

        if not wallet_amount > 0:
            response = {
                'status': 'FAIL',
                'ret_status': status.HTTP_400_BAD_REQUEST,
                'message': 'Insufficient Balance'
            }

            return response

        response['message'] = 'Amount debited successfully'

    response['ret_status'] = status.HTTP_200_OK

    response['balance'] = wallet_amount
    response['wallet'] = wallet

    return response

def get_wallet_for_user(user):
    response = {}
    try:
        wallet = Wallet.objects.get(user=user)
        response['ret_status'] = status.HTTP_200_OK
        response['wallet'] = wallet
        return response
    except ObjectDoesNotExist:
        response = {
            'status': 'FAIL',
            'ret_status': status.HTTP_400_BAD_REQUEST,
            'message': 'No wallet found for you'
        }

        return response
