from django.db import transaction

from rest_framework import status, views
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from users.models import User
from users.helpers import *
from users.permissions import CsrfExemptSessionAuthentication
from wallet.helpers import create_wallet_for_user


# Create your views here.
class UserLogin(views.APIView):
    """
    User Authentication to be done here and the response with the
    user token to be provided.

    """
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        print("This is the data  : ", data)
        email = data.get("email").strip()
        password = data.get("password").strip()

        login_response = User.objects.do_login(
            request=request, email=email, password=password)

        if login_response.status_code == status.HTTP_200_OK:
            user = login_response.data.get('user')
            token = login_response.data.get('token')
            response = {
                'status': True,
                'message': {
                    'name': user.name,
                    'email': user.email,
                    'mAuthToken': token,
                }
            }

            return Response(status=status.HTTP_200_OK, data=response, content_type='text/html; charset=utf-8')

        response = {
            'text': login_response.data
        }
        return Response(status=login_response.status_code, data=response, content_type='text/html; charset=utf-8')


class UserSignup(views.APIView):
    """
    Registration of the new user for accessing the wallet
    """
    permission_classes = (AllowAny,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        """
        Creating the new user along with the wallet
        :param request: A dict of the format
            {
                "email": "xyz@gmail.com",
                "password": "1234",
                "phone": "7867898798",
                "name": "xyz"
            }

        :return: Below is the response if provided with valid request
                {
                    'name': 'Name of the user',
                    'email': 'email of the user',
                    'mAuthToken': 'authorization token',
                }
        """
        data = request.data

        response = {
            'status': False,
            'message': {
                'text': '',
            }
        }

        try:
            data = validate_user_data(data, response)
        except ValidationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=e.args[0])

        with transaction.atomic():
            try:
                user = User.objects.create_user(**data)
            except Exception as e:
                transaction.set_rollback(True)
                response['message'] = e.args[0]
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data=response)

            login_response = User.objects.do_login(request=request, user=user)

            if login_response.status_code != status.HTTP_200_OK:
                transaction.set_rollback(True)
                return Response(status=login_response.status_code,
                                data=login_response.data)

            token = login_response.data.get('token')

            new_wallet = create_wallet_for_user(user)

            if not new_wallet.get('ret_status') == status.HTTP_201_CREATED:
                transaction.set_rollback(True)
                print("Transaction rollback is done before this")
                return Response(status=new_wallet['ret_status'],
                                data=new_wallet)

        response['status'] = True
        response['message'] = {
            'name': user.name,
            'email': user.email,
            'mAuthToken': token,
        }
        return Response(status=status.HTTP_200_OK, data=response,
                        content_type='text/html; charset=utf-8')
