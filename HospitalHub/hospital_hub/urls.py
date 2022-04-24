"""
Definition of urls for hospital_hub.
"""

from django.urls import path ,include
from django.contrib import admin
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    #########################
    #paths for owner

    #example :        path('/Onwer/Hoapitals', views.logowner, name='onwer_login'),
    #example :        path('/Onwer/home', views.index, name='onwer_home'),



    #########################
    #paths for admin
    path('admin/home', views.AdminHome,name='admin_home'),




    #########################
    #paths for doctor





    #########################
    #paths for patient


]
