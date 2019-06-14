from django.contrib import admin
from django.urls import path
from .views import JokesBotView, MessengerProfile, Testing, firstStep, secondStep, thirdstep, fourthStep

urlpatterns = [
   path('', JokesBotView.as_view(), name="parsetext"),
   path('/profile', MessengerProfile.as_view(), name="profile"),
   path('/test', Testing.as_view(), name="test"),
   path('/first', firstStep, name="Demo1"),
   path('/second', secondStep, name="Demo2"),
   path('/third', thirdstep, name="Demo3"),
   path('/four', fourthStep, name="Demo4")

]
