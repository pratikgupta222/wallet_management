import re
import phonenumbers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings


def validate_phone_number(phone_number):
    """
    Validation Rule for the phone number used are as below:
        - Phone number should be of exactly 10 digits
        - Phone number can start with digits 6,7,8 or 9

    :param phone_number: phone number
    :return: phone number if it is valid
    """
    phn_exp = re.compile(r"^[6-9]\d{9}$")
    match = phn_exp.match(phone_number)
    if match is not None:
        return phone_number
    else:
        return False


def validate_user_email(email):
    """
    Validating the format of the email

    :param email: email to be validated
    :return: True if the email is valid
    """
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def validate_name(name):
    """
    :param name: Name to be validated
    :return: name if it is valid else False
    """
    # Name should be only alphabetic and can have only single space between
    # adjacent words
    reg_exp = re.compile(r"^([A-Za-z]){1}( ?[A-Za-z]){1,}$", re.IGNORECASE)
    match = reg_exp.match(name)
    if match is not None:
        return name
    else:
        return False


def validate_user_data(data, response):
    """
    Validating the data provided for the new user
    :param data: A dict of the format
            {
                "email": "xyz@gmail.com",
                "password": "1234",
                "phone": "7867898798",
                "name": "xyz"
            }

    :param response:
    :return: Error if any of the parameter is not in the correct
     format else the dictionary of key , value pair
    """

    email = data.get('email', None)
    password = data.get('password', None)
    phone_number = data.get('phone', None)
    name = data.get('name', None)
    dict_ = {}

    if not email or not password:
        response['message'] = 'email and password required'
        raise ValidationError(response)

    data['email'] = email.lower()
    if not validate_user_email(email):
        response['message'] = 'Please, Provide a valid email'
        raise ValidationError(response)

    if not (phone_number and validate_phone_number(phone_number)):
        response['message'] = 'Please, Provide a valid Phone number'
        raise ValidationError(response)

    data['phone'] = phonenumbers.parse(phone_number, settings.DEFAULT_COUNTRY.get('country_code'))

    if name:
        if not validate_name(name):
            raise ValidationError("Please Enter a valid Owner name")

    data['is_active'] = True

    return data
