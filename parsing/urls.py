from django.contrib import admin
from django.urls import path
from .views import JokesBotView, MessengerProfile

urlpatterns = [
   path('', JokesBotView.as_view(), name="parsetext"),
   path('/profile', MessengerProfile.as_view(), name="profile")
]
