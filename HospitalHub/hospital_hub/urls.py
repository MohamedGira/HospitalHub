"""
Definition of urls for hospital_hub.
"""

from django.urls import path ,include
from django.contrib import admin
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('logout', views.Logout, name='user_logout'),
    #########################
    #paths for owner

    #example :        path('/Onwer/Hoapitals', views.logowner, name='onwer_login'),
    #example :        path('/Onwer/home', views.index, name='onwer_home'),



    #########################
    #paths for admin
    path('admin', views.Admin.AdminLogin,name='admin_login'),
    path('admin/login', views.Admin.AdminLogin,name='admin_login'),
    path('admin/home', views.Admin.AdminHome,name='admin_home'),
    path('admin/logout', views.Admin.AdminLogout,name='admin_logout'),
    path('admin/add_admin', views.Admin.AddAdmin,name='admin_add_admin'),
    path('admin/add_speciality', views.Admin.AddSpeciality,name='add_speciality'),
    path('admin/specialities',views.Admin.ViewSpecialities,name='view_specialities'),
    path('admin/admins',views.Admin.AdminHome,name='admin_view_admins'),
    path('admin/doctors',views.Admin.AdminHome,name='admin_view_doctors'),
   

    #########################
    #paths for doctor





    #########################
    #paths for patient

     path('patient/login', views.Patient.PatientLogin,name='patient_login'),
     path('patient/register', views.Patient.PatientRegister,name='patient_register'),
     path('patient/home', views.Patient.PatientHome,name='patient_home'),
]
