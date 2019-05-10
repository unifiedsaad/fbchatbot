from django.contrib import admin
from django.urls import path
from .views import JokesBotView

urlpatterns = [
   path('', JokesBotView.as_view(), name="parsetext")
]
