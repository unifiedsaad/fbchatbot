from django.contrib import admin
from django.urls import path
from .views import YoMamaBotView

urlpatterns = [
   path('', YoMamaBotView.as_view(), name="parsetext")
]
