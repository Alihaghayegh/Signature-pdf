from django.urls import path, include
from rest_framework import routers

from . import views

app_name = "UserInfo"


urlpatterns = [
    path('hello/' , views.hello_world),
    path('user-list/' , views.users_list),
    path('user/<int:id>' , views.user_view),
    path('user/create' , views.user_create),
]
