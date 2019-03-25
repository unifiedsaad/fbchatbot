from django.contrib import admin
from django.urls import path
from .views import parse

urlpatterns = [
   path('', parse, name="parsetext")
]
