# Simple Wallet

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://github.com/pratikgupta222/wallet_management)

Simple Wallet is small wallet management system with below Features

  - Own wallet for each users
  - Allowing Wallet transactions(Credit/Debit)
  - 

### Installation

The first thing to do is to clone the repository:
```
$ git clone https://github.com/pratikgupta222/wallet_management.git
$ cd wallet_management
```

Create a virtualenv with Python 3:
```
$ virtualenv -p python3 venv
$ source venv/bin/activate
```

Upgrade pip
```
$ pip3 install --upgrade pip
```
Install the dependencies
```
(venv)$ pip3 install -r requirements/local.txt
```

Note the (venv) in front of the prompt. This indicates that this terminal session operates in a virtual environment.

Once pip has finished downloading the dependencies:
```
(venv)$ cd wallet_management
(venv)$ python manage.py runserver
```
And navigate to http://127.0.0.1:8000/users/signup.
