"""
Definition of urls for hospital_hub.
"""

from django.urls import path ,include
from django.contrib import admin
from . import views


urlpatterns = [
    path('', views.index, name='home'),
]
