from django.contrib import admin
from django.urls import path
from .views import JokesBotView, MessengerProfile, Testing

urlpatterns = [
   path('', JokesBotView.as_view(), name="parsetext"),
   path('/profile', MessengerProfile.as_view(), name="profile"),
   path('/test', Testing.as_view(), name="test"),

]
