"""
Definition of urls for hospital_hub.
"""

from django.urls import path, include
from django.contrib import admin
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('', views.index, name='patient_home'),
    path('logout', views.Logout, name='user_logout'),
    path('login', views.Login, name='login'),
    path('l', views.Login, name='login'),


    #########################
    # paths for owner

    path('owner/register', views.Owner.OwnerRegister, name='owner_register'),
    path('owner/login', views.Owner.OwnerLogin, name='owner_login'),
    path('owner/logout', views.Owner.OwnerLogout, name='owner_logout'),
    path('owner/home', views.Owner.OwnerHome, name='owner_home'),
    path('o', views.Owner.OwnerHome, name='owner_home'),
    path('owner/add_admin', views.Owner.OwnerAddAdmin, name='owner_add_admin'),
    path('owner/add_hospitals', views.Owner.OwnerAddHospitals,
         name='owner_add_hospitals'),
    path('owner/view_hospitals', views.Owner.OwnerViewHospitals,
         name='owner_view_hospitals'),
    path('owner/specialities/<int:hospital_id>',
         views.Owner.OwnerViewSpecialities, name='owner_view_specialities'),
    path('owner/specialities/<int:hospital_id>/<str:speciality_name>',
         views.Owner.OwnerViewSpeciality, name='owner_view_speciality'),
    path('owner/doctors/<str:doctor_name>',
         views.Owner.OwnerViewDoctorProfile, name='owner_view_doctor'),
    path('owner/Hospitals/remove/<int:hospital_id>',
         views.Owner.RemoveHospital, name='remove_hospital'),






    #########################
    # paths for admin
    path('a', views.Admin.AdminLogin, name='admin_login'),

    path('admin', views.Admin.AdminLogin, name='admin_login'),
    path('admin/login', views.Admin.AdminLogin, name='admin_login'),
    path('admin/home', views.Admin.AdminHome, name='admin_home'),
    path('admin/logout', views.Admin.AdminLogout, name='admin_logout'),
    path('admin/add_admin', views.Admin.AddAdmin, name='admin_add_admin'),
    path('admin/add_speciality', views.Admin.AddSpeciality, name='add_speciality'),
    path('admin/add_doctor', views.Admin.AddDoctor, name='add_doctor'),
    path('admin/admins', views.Admin.ViewAdmins, name='admin_view_admins'),
    path('admin/admins/remove/<int:removed_admin_id>',
         views.Admin.RemoveAdmin, name='remove_admin'),
    path('admin/doctors', views.Admin.ViewDoctors, name='admin_view_doctors'),
    path('admin/doctors/remove/<int:doctor_id>',
         views.Admin.RemoveDoctorFromDoctors, name='remove_doctor_from_doctors'),
    path('admin/doctors/<str:doctor_name>',
         views.Admin.ViewDoctorProfile, name='admin_view_doctor'),
    path('admin/specialities', views.Admin.ViewSpecialities,
         name='view_specialities'),
    path('admin/specialities/remove/<int:speciality_id>',
         views.Admin.RemoveSpeciality, name='remove_speciality'),
    path('admin/specialities/<str:speciality>',
         views.Admin.ViewSpeciality, name='view_speciality'),
    path('admin/specialities/speciality/remove_doctor/<int:doctor_id>',
         views.Admin.RemoveDoctorFromSpeciality, name='remove_doctor_from_speciality'),


    #########################
    # paths for doctor
    path('Doctor/register', views.Doctor.DoctorRegister, name='doctor_register'),
    path('Doctor/login', views.Doctor.DoctorLogin, name='doctor_login'),
    path('Doctor/logout', views.Doctor.DoctorLogout, name='doctor_logout'),
    # displaying schedual and some other data
    path('Doctor/profile', views.Doctor.DoctorProfile, name='doctor_profile'),
    path('Doctor/dashboard', views.Doctor.DoctorDashboard, name='doctor_dashboard'),
    #path('Doctor/schedule', views.Doctor.DoctorSchedule, name='doctor_schedule'),
    path('Doctor/ViewRecord/<str:patient_name>', views.Doctor.DoctorViewRecord,
         name='doctor_viewRecord'),
    path('Doctor/ViewHistory/<str:patient_name>', views.Doctor.ViewMedicalHistory,
         name='doctor_view_history'),

    path('Doctor/AcceptEmployment/<str:doctor_name>',
         views.Doctor.DoctorAccept, name='doctor_employment_success' ),
    path('Doctor/RejectEmployment/<str:doctor_name>',
         views.Doctor.DoctorReject,name='doctor_employment_failure'),

    #########################
    # paths for patient

    path('patient/login', views.Patient.PatientLogin, name='patient_login'),
    path('patient/register', views.Patient.PatientRegister, name='patient_register'),
    path('patient/home', views.Patient.PatientHome, name='patient_home'),
    path('patient/logout', views.Patient.patientlogout, name='patient_logout'),

    path('patient/searchbyspeciality',
         views.Patient.searchbyspeciality, name='specialities_search'),
    path('patient/find_hospitals_by_speciality',
         views.Patient.find_hospitals_by_speciality, name='find_hospitals_by_speciality'),
    path('patient/book_appointment/<str:doctor_name>',
         views.Patient.ViewDoctorProfile, name='book_appointment'),

    path('patient/view_doctors',views.Patient.ViewDoctors, name='patient_view_doctors'),
    path('patient/view_specialities',views.Patient.ViewSpecialities, name='patient_view_specialities'),
    path('patient/view_specialities/<str:speciality_name>',views.Patient.PatientViewSpeciality, name='patient_view_speciality'),
    path('patient/view_hospitals',views.Patient.ViewHospitals, name='patient_view_hospitals'),
    path('patient/view_hospitals/<int:hospital_id>',views.Patient.PatientViewHospital, name='patient_view_hospital'),
    path('patient/view_hospitals/<int:hospital_id>/<str:speciality_name>',views.Patient.PatientViewHospitalSpeciality, name='patient_view_hospital_speciality'),
    
    path('patient/appointments',views.Patient.ViewAppointments, name='patient_view_appointments'),
    path('patient/appointments/<int:appt_id>',views.Patient.ViewAppointmentDocs, name='patient_view_appointments_docs'),
    path('patient/ViewRecord', views.Patient.PatientViewRecord,name='patient_viewRecord'),
]
