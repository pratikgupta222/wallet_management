from django.urls import path
from users import views

urlpatterns = [
    path('users/login', views.UserLogin.as_view(), name='user-login'),
    path('users/signup', views.UserSignup.as_view(), name='user-signup'),
]
