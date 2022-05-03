from datetime import datetime
import site
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from .models import *
from .models import Patient as PatientModel
from .models import Admin as AdminModel
from .models import Doctor as DoctorModel
from .models import Owner as OwnerModel
from .models import Speciality as SpecialityModel
from .models import Hospital as HospitalModel
from .models import City as CityModel
from .utils import *

import re

##
from django.contrib import messages
##
import logging

logging.basicConfig(level=logging.DEBUG)

User = get_user_model()
# Create your views here.


def index(request):
    if not request.user.is_authenticated:
        return render(request, "hospital_hub/index.html")
    else:
        if request.user.is_admin:
            return HttpResponseRedirect(reverse('admin_home'))
        else:
            return HttpResponseRedirect(reverse('patient_home'))
#       elif request.user.is_doctor:
#            return HttpResponseRedirect(reverse('admin_home'))

    return render(request, "hospital_hub/index.html")


def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


def Login(request):
    # redirect users to home page if they are already signed in as patients
    if request.user.is_authenticated:  # if already signed in
        if request.user.is_doctor:
            return HttpResponseRedirect(reverse('doctor_home'))
        if request.user.is_patient:
            return HttpResponseRedirect(reverse('patient_home'))
        logout(request)
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':
        username = request.POST.get("username", None)
        password = request.POST.get("password", None)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if request.POST['user_type'] == "doctor":
                if user.is_doctor:
                    login(request, user)
                    return HttpResponseRedirect(reverse("doctor_home"))
                else:
                    return render(request, "hospital_hub\login-general.html", {
                        "message": "Invalid username or password",
                        "radio": "doctor"
                    })
            elif request.POST['user_type'] == "patient":
                if user.is_patient:
                    login(request, user)
                    return HttpResponseRedirect(reverse("patient_home"))
                else:
                    return render(request, "hospital_hub\login-general.html", {
                        "message": "Invalid username or password",
                        "radio": "patient"
                    })
            else:
                return render(request, "hospital_hub\login-general.html", {
                    "message": "Something went wrong, try again",
                    "radio": "patient"
                })
        else:
            return render(request, "hospital_hub\login-general.html", {
                "message": "Invalid username or password",
                "radio": "patient"
            })
    else:
        return render(request, "hospital_hub\login-general.html", {
            "radio": "patient"
        })


############################################################################
# Owner app

class Owner:

    def OwnerRegister(request):
        if request.method == "POST":
            username = request.POST["username"]
            full_name = request.POST["full_name"]
            email = request.POST["email"]
            password = request.POST["password"]
            confirm_password = request.POST["confirm_password"]
            city = request.POST["city"]
            phone_number = request.POST["phone_number"]
            if password != confirm_password:
                return render(request, "owner_register", {
                    "message": "Passwords must match."})

        # Attempt to create new user
            try:
                selectedCity = CityModel.objects.filter(id=city).first()
                user = User.objects.create_user(username, email, full_name, password,
                                                is_owner=True, city=selectedCity, phone_number=phone_number)
                user.save()
                owner = OwnerModel(my_account=user)
                owner.save()

            except IntegrityError:
                return render(request, "hospital_hub/Owner/owner_register.html", {
                    "message": "Username already taken."
                })
            login(request, user)  # Checks authentication
            return HttpResponseRedirect(reverse("owner_home"))
        else:
            cities = CityModel.objects.all()
            return render(request,
                          "hospital_hub/Owner/owner_register.html", {
                              "cities": cities
                          })

    # Owner Owner signin/signout methods__________________________________________________________________________________

    def OwnerLogin(request):
        # Redirect users to home page if they are already signed in as owners
        if request.user.is_authenticated:
            if request.user.is_owner:
                return HttpResponseRedirect(reverse('owner_home'))

        if request.method == "POST":
            # Attempt to sign user in
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)

            # Check if authentication successful
            if user is not None:
                # Check if the user is owner
                if user.is_owner:
                    login(request, user)
                    return HttpResponseRedirect(reverse("owner_home"))
                else:
                    return render(request, "hospital_hub/owner/owner_login.html", {
                        "message": "Invalid username or password",
                        "submitted_username": username,
                    })
            else:
                return render(request, "hospital_hub/Owner/owner_login.html", {
                    "message": "Invalid  username or password",
                    "submitted_username": username,
                })
        else:
            return render(request, "hospital_hub/Owner/owner_login.html")

    def OwnerLogout(request):
        logout(request)
        return HttpResponseRedirect(reverse('owner_login'))

    # Owner main methods__________________________________________________________________________________

    def OwnerHome(request):
        # Redirect users to login page if they are not signed in as owners
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('owner_login'))
        elif not request.user.is_owner:
            return HttpResponseRedirect(reverse('home'))
        return render(request, "hospital_hub/Owner/owner_home.html")

    def OwnerAddAdmin(request):  # register new admin to my hospital
        # Redirect users to login page if they are not signed in as admins
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('owner_login'))
        elif not request.user.is_owner:
            # may add later "you have no access to this page :( "
            return HttpResponseRedirect(reverse('home'))

        cities = City.objects.all()

        if(request.method == "POST"):
            username = request.POST["username"]
            full_name = request.POST["full_name"]
            email = request.POST["email"]
            password = request.POST["password"]
            confirm_password = request.POST["confirm_password"]
            city = request.POST["city"]
            phone_number = request.POST["phone_number"]

            if password != confirm_password:
                return render(request, "hospital_hub/admin/add_admin.html", {
                    "mustmatch": "Passwords must match.",
                    "username": username,
                    "email": email,
                    "full_name": full_name,
                    "password": password,
                    "cities": cities,
                    "provided_city": city,
                    "phone": phone_number,
                })

            image = request.FILES.get('image', None)
            print(image)

            # Attempt to create new user
            try:
                cit = City.objects.get(id=city)
                if image is not None:
                    user = User.objects.create_user(username, email, full_name,
                                                    password, is_admin=True, city=cit, phone_number=phone_number, image=image)
                else:
                    user = User.objects.create_user(username, email, full_name,
                                                    password, is_admin=True, city=cit, phone_number=phone_number)
                admin = AdminModel(my_account=user)
                user.save()
                # links admin toadmin object
                admin.save()
            except IntegrityError:
                return render(request,  "hospital_hub/admin/add_admin.html", {
                    "mustmatch": "Username or email are already taken.",
                    "full_name": full_name,
                    "cities": cities,
                    "city": city,
                    "phone_number": phone_number,
                    "email": email,
                })
            return HttpResponseRedirect(reverse("owner_home"))
        else:

            return render(request, "hospital_hub/admin/add_admin.html", {
                "cities": cities,
            })

    def OwnerAddHospital(request):  # register new  hospital
        # Redirect users to login page if they are not signed in as admins
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('owner_login'))
        elif not request.user.is_owner:
            # may add later "you have no access to this page :( "
            return HttpResponseRedirect(reverse('home'))

        cities = City.objects.all()
        admins = AdminModel.objects.filter(hospital=None)
        adminaccounts = []
        for admin in admins:
            adminaccounts.append(admin.my_account)

        if(request.method == "POST"):
            hospital_name = request.POST["hospital_name"]
            city = request.POST["city"]
            admin_account_id = request.POST["admin_account_id"]

            image = request.FILES.get('image', None)

            # Attempt to create new hospital

            cit = City.objects.get(id=city)
            if image is not None:
                hospital = HospitalModel(
                    name=hospital_name, city=cit, image=image)
            else:
                hospital = HospitalModel(name=hospital_name, city=cit)

            hospital.save()
            admin_set = User.objects.filter(
                id=int(admin_account_id), admin=True)
            if admin_set.count() == 1:
                admin = admin_set.first().my_admin.first()
                admin.hospital = hospital
                admin.save()
                return HttpResponseRedirect(reverse("owner_home"))
            else:
                return render(request, "hospital_hub/owner/add_hospital.html", {
                    "admins": adminaccounts,
                    "message": "Admin Doesn't exist",
                    "cities": cities,
                    "provided_name": hospital_name,
                    "provided_city": cit,
                    # "provided_admin":
                })
        else:

            return render(request, "hospital_hub/owner/add_hospital.html", {
                "admins": adminaccounts,
                "cities": cities,
            })


############################################################################
# Admin app

class Admin:

    # Admin signin/signout methods__________________________________________________________________________________

    def AdminLogin(request):
        # Redirect users to home page if they are already signed in as admins
        if request.user.is_authenticated:
            if request.user.is_admin:
                return HttpResponseRedirect(reverse('admin_home'))

        if request.method == "POST":
            # Attempt to sign user in
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)

            # Check if authentication successful
            if user is not None:
                # Check if the user is admin
                if user.is_admin:
                    login(request, user)
                    return HttpResponseRedirect(reverse("admin_home"))
                else:
                    return render(request, "hospital_hub/admin/admin_login.html", {
                        "message": "Invalid username or password",
                        "submitted_username": username,
                    })
            else:
                return render(request, "hospital_hub/Admin/admin_login.html", {
                    "message": "Invalid  username or password",
                    "submitted_username": username,
                })
        else:
            return render(request, "hospital_hub/Admin/admin_login.html")

    def AdminLogout(request):
        logout(request)
        return HttpResponseRedirect(reverse('admin_login'))

    # Admin main methods__________________________________________________________________________________

    def AdminHome(request):
        # Redirect users to login page if they are not signed in as admins
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('admin_login'))
        elif not request.user.is_admin:
            # may add later "you have no access to this page :( "
            return HttpResponseRedirect(reverse('home'))
        return render(request, "hospital_hub/Admin/admin_home.html")

    def AddAdmin(request):  # register new admin to my hospital
        # Redirect users to login page if they are not signed in as admins
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('admin_login'))
        elif not request.user.is_admin:
            # may add later "you have no access to this page :( "
            return HttpResponseRedirect(reverse('home'))

        cities = City.objects.all()

        if(request.method == "POST"):
            username = request.POST["username"]
            full_name = request.POST["full_name"]
            email = request.POST["email"]
            password = request.POST["password"]
            confirm_password = request.POST["confirm_password"]
            city = request.POST["city"]
            phone_number = request.POST["phone_number"]
            # only one admin related to this account
            hospital = request.user.my_admin.first().hospital

            if password != confirm_password:
                return render(request, "hospital_hub/admin/add_admin.html", {
                    "mustmatch": "Passwords must match.",
                    "username": username,
                    "email": email,
                    "full_name": full_name,
                    "password": password,
                    "cities": cities,
                    "provided_city": city,
                    "phone": phone_number,
                })

            image = request.FILES.get('image', None)
            print(image)

            # Attempt to create new user
            try:
                cit = City.objects.get(id=city)
                if image is not None:
                    user = User.objects.create_user(username, email, full_name,
                                                    password, is_admin=True, city=cit, phone_number=phone_number, image=image)
                else:
                    user = User.objects.create_user(username, email, full_name,
                                                    password, is_admin=True, city=cit, phone_number=phone_number)
                user.save()
                # links admin toadmin object
                admin = AdminModel(my_account=user, hospital=hospital)
                admin.save()
            except IntegrityError:
                return render(request,  "hospital_hub/admin/add_admin.html", {
                    "mustmatch": "Username or email are already taken.",
                    "full_name": full_name,
                    "cities": cities,
                    "city": city,
                    "phone_number": phone_number,
                    "email": email,
                })
            return HttpResponseRedirect(reverse("admin_home"))
        else:

            return render(request, "hospital_hub/admin/add_admin.html", {
                "cities": cities,
            })

    def AddSpeciality(request):
        # Redirect users to login page if they are not signed in as admins
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('admin_login'))
        elif not request.user.is_admin:
            # may add later "you have no access to this page :( "
            return HttpResponseRedirect(reverse('home'))

        specialities = Speciality.objects.all()
        if request.method == "POST":
            # check if input is valid
            speciality = Speciality.objects.filter(
                name=request.POST["speciality"]).first()
            if speciality is not None:
                hospital = request.user.my_admin.first().hospital
                # check if hospital haven't already added this speciality
                if hospital.specialities.filter(name=speciality.name).count() == 0:
                    hospital.specialities.add(speciality)
                    hospital.save()
                    return HttpResponseRedirect(reverse("admin_home"))
                else:
                    return render(request, "hospital_hub/Admin/add_speciality.html", {
                        "specialities": specialities,
                        "submitted_speciality_name": request.POST["speciality"],
                        "provided_spec": hospital.specialities.filter(name=speciality.name).first(),
                        "message": "This speciality is already added to yout hospital"})
            else:
                return render(request, "hospital_hub/Admin/add_speciality.html", {
                    "specialities": specialities,
                    "message": "Invalid Input"})

        return render(request, "hospital_hub/Admin/add_speciality.html", {
            "specialities": specialities,
        })

    def ViewSpecialities(request):
        # Redirect users to login page if they are not signed in as admins
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('admin_login'))
        elif not request.user.is_admin:
            # may add later "you have no access to this page :( "
            return HttpResponseRedirect(reverse('home'))

        hospital = request.user.my_admin.first().hospital
        specialities = hospital.specialities.all()

        specialities_with_doctors_dependet = []
        for speciality in specialities:
            doctors = DoctorModel.objects.filter(
                hospital=hospital, speciality=speciality)
            specialities_with_doctors_dependet.append([speciality, doctors])

        if specialities.count() == 0:
            return render(request, "hospital_hub/Admin/view_specialities.html", {
                "specialities": None,
                "hospital_name": request.user.my_admin.first().hospital.name,
                #   "hospital_name":hospital.name,
            })
        else:
            return render(request, "hospital_hub/Admin/view_specialities.html", {
                "specialities": specialities_with_doctors_dependet,
                "hospital_name": request.user.my_admin.first().hospital.name,

                #   "hospital_name":hospital.name,
            })

    def ViewSpeciality(request, speciality):
        hospital = request.user.my_admin.first().hospital
        spec = Speciality.objects.filter(name=speciality)
        if spec.count() == 1:
            doctors = DoctorModel.objects.filter(
                speciality=spec.first(), hospital=hospital)

    def ViewSpeciality(request, speciality):
        hospital = request.user.my_admin.first().hospital
        spec = Speciality.objects.filter(name=speciality)
        if spec.count() == 1:
            doctors = DoctorModel.objects.filter(
                speciality=spec.first(), hospital=hospital)
            doctors_with_dependent_appointmens = []
            for doctor in doctors:
                doctors_with_dependent_appointmens.append(
                    [doctor, doctor.appointments.all()])

            return render(request, "hospital_hub/admin/view_speciality.html", {
                "doctors": doctors_with_dependent_appointmens,
                "hospital_name": request.user.my_admin.first().hospital.name,
                "speciality": spec.first().name
            })
        else:
            specialities = hospital.specialities.all()
            return render(request, "hospital_hub/admin/view_specialities.html", {
                "message": "Requested specialitiy doesn't exitst",
                "specialities": specialities,
                "hospital_name": request.user.my_admin.first().hospital.name,

            })

    def ViewDoctorProfile(request, doctor_name):
        days = ['Sunday', 'Saturday', 'Monday',
                'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        hospital = request.user.my_admin.first().hospital
        doc_account = User.objects.filter(username=doctor_name, doctor=True)
        doctor = doc_account.first().my_doctor.first()
        if request.method == "POST":
            if request.POST.get("command", False):

                for day in days:
                    if request.POST['command'] == "edit_"+day:
                        schedule_day = Schedule.objects.filter(
                            doctor=doctor, day=day).first()
                        schedule_day.start_time = request.POST['new_start']
                        schedule_day.end_time = request.POST['new_end']
                        schedule_day.save()
                        return HttpResponseRedirect(reverse('admin_view_doctor', args=[doctor_name]))

                for day in days:
                    if request.POST['command'] == "remove_"+day:
                        schedule_day = Schedule.objects.filter(
                            doctor=doctor, day=day).first()
                        if schedule_day.appointments.all().count() == 0:
                            schedule_day.delete()
                            return HttpResponseRedirect(reverse('admin_view_doctor', args=[doctor]))
                        else:
                            return HttpResponseRedirect(reverse('admin_view_doctor', args=[doctor]) +
                                                        '?message=+'+day+' is busy, couldn\'t remove')

                if request.POST['command'] == "add_day":
                    if Schedule.objects.filter(doctor=doctor, day=request.POST['to_add']).count() == 0:
                        schedule = Schedule(doctor=doctor, day=request.POST['to_add'],
                                            start_time=request.POST['start_time'],
                                            end_time=request.POST['end_time'],
                                            price=request.POST['price'],
                                            patient_count=request.POST['max_patient_count'])
                        schedule.save()
                        return HttpResponseRedirect(reverse('admin_view_doctor', args=[doctor]))

                    return HttpResponseRedirect(reverse('admin_view_doctor', args=[doctor]) +
                                                '?message=A Schedule exists on day already, you can Edit it below')

        if doc_account.count() == 1:
            doc = doc_account.first().my_doctor.first()
            account = doc_account.first()
            reviews = doc.my_reviews.all()
            schedules = doc.dailyschedule.all()
            schedule_abbreviation = []

            for schedule in schedules:
                schedule_abbreviation.append([schedule, schedule.day[0:3]])
            empty_days = []
            for day in days:
                dne = True
                for schedule in schedules:
                    if schedule.day == day:
                        dne = False
                        break
                if dne == True:
                    empty_days.append(day)

            return render(request, "hospital_hub/admin/admin_view_doctor_profile.html", {
                "doctor": doc,
                "account": account,
                "hospital": hospital,
                "schedules": schedule_abbreviation,
                "reviews": reviews,
                "empty_days": empty_days,

            })
        else:
            specialities = hospital.specialities.all()
            return render(request, "hospital_hub/admin/view_specialities.html", {
                "message": "No doctor by this name exitsts in your hospital.",
                "specialities": specialities,
            })

    def ViewDoctors(request):
        hospital = request.user.my_admin.first().hospital
        doctors = DoctorModel.objects.filter(hospital=hospital)
        doctors_with_dependent_appointmens = []
        for doctor in doctors:
            doctors_with_dependent_appointmens.append(
                [doctor, doctor.appointments.all()])

        return render(request, "hospital_hub/admin/view_doctors.html", {
            "doctors": doctors_with_dependent_appointmens,
            "hospital_name": request.user.my_admin.first().hospital.name,
            "flag": "all"
        })

    def AddDoctor(request):
        days = ['Sunday', 'Saturday', 'Monday',
                'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        gdoctors = DoctorModel.objects.filter(is_employed=False)
        specialities = request.user.my_admin.first().hospital.specialities.all()
        gdoctors_accounts = []
        for doc in gdoctors:
            gdoctors_accounts.append(doc.my_account)

        if request.method == "GET":

            if request.GET.get('speciality'):
                speciality = Speciality.objects.filter(
                    name=request.GET['speciality'])
                if speciality.count() == 1:
                    doctors = DoctorModel.objects.filter(
                        is_employed=False, speciality=speciality.first())
                    doctors_accounts = []
                    for doc in doctors:
                        doctors_accounts.append(doc.my_account)
                    if len(doctors_accounts) > 0:
                        return render(request, "hospital_hub/Admin/add_doctor.html", {
                            "specialities": specialities,
                            "submitted_speciality_name": request.GET['speciality'],
                            "doctors": doctors_accounts,
                            "days": days,
                        })
                    else:
                        return render(request, "hospital_hub/Admin/add_doctor.html", {
                            "specialities": specialities,
                            "doctors": None,
                            "submitted_speciality_name": request.GET['speciality'],
                            "doctor_list_message": "No Avalable doctors in this speciality",
                            "days": days
                        })
                else:
                    return render(request, "hospital_hub/Admin/add_doctor.html", {
                        "specialities": specialities,
                        "doctors": gdoctors_accounts,
                        "message": "Invalid specialty submitted",
                        "days": days
                    })
            else:
                return render(request, "hospital_hub/Admin/add_doctor.html", {
                    "specialities": specialities,
                    "doctors": None,
                    "doctor_list_message": "Choose speciality in order to display availble doctors",
                    "days": days
                })

        elif request.method == "POST":
            doctor_email = request.POST["doctor_email"]
            userset = User.objects.filter(email=doctor_email, doctor=True)
            if userset.count() == 1:
                doctor = userset.first().my_doctor.first()
                weekly_schedule = []
                for day in days:
                    if day in request.POST:
                        s = Schedule(day=day,
                                     doctor=doctor,
                                     start_time=request.POST[(day+"1")],
                                     end_time=request.POST[(day+"2")],
                                     price=int(request.POST["price"]),
                                     patient_count=10)
                        weekly_schedule.append(s)

                doctor.is_employed = True
                doctor.hospital = request.user.my_admin.first().hospital
                doctor.save()
                for s in weekly_schedule:
                    s.save()
                return HttpResponseRedirect(reverse('view_specialities'))
            else:
                return render(request, "hospital_hub/Admin/add_doctor.html", {
                    "specialities": specialities,
                    "doctors": gdoctors_accounts,
                    "days": days,
                    "message": "Invalid doctor input"
                })

    def ViewAdmins(request):
        hospital = request.user.my_admin.first().hospital
        admins = AdminModel.objects.filter(hospital=hospital)
        lower_admins = AdminModel.objects.filter(
            hospital=hospital, id__gt=request.user.my_admin.first().id)
        higher_admins = AdminModel.objects.filter(
            hospital=hospital, id__lt=request.user.my_admin.first().id)

        if len(lower_admins)+len(higher_admins) == 0:
            return render(request, "hospital_hub/Admin/view_admins.html", {
                "hospital_name": hospital.name,
                "lower_admins": lower_admins,
                "higher_admins": higher_admins,
                "empty": "No other admins exists"
            })
        return render(request, "hospital_hub/Admin/view_admins.html", {
            "hospital_name": hospital.name,
            "lower_admins": lower_admins,
            "higher_admins": higher_admins,
        })

    def RemoveAdmin(request, removed_admin_id):
        adminset = AdminModel.objects.filter(id=removed_admin_id)
        if adminset.count() == 1:
            admin = adminset.first()
            if removed_admin_id > request.user.my_admin.first().id:
                account = admin.my_account
                admin.delete()
                account.delete()
                return HttpResponseRedirect(reverse('admin_view_admins'))
            else:
                hospital = request.user.my_admin.first().hospital
                admins = AdminModel.objects.filter(hospital=hospital)
                lower_admins = []
                higher_admins = []
                for admin in admins:
                    if admin.id < request.user.my_admin.first().id:
                        higher_admins.append([admin, admin.my_account])
                    elif admin.id > request.user.my_admin.first().id:
                        lower_admins.append([admin, admin.my_account])
                if len(lower_admins)+len(higher_admins) == 0:
                    return render(request, "hospital_hub/Admin/view_admins.html", {
                        "hospital_name": hospital.name,
                        "message": "Couldn't remove this admin",
                        "empty": "No other admins exists"
                    })
                return render(request, "hospital_hub/Admin/view_admins.html", {
                    "hospital_name": hospital.name,
                    "lower_admins": lower_admins,
                    "higher_admins": higher_admins,
                    "message": "Couldn't remove this admin",
                })
        else:
            hospital = request.user.my_admin.first().hospital
            admins = AdminModel.objects.filter(hospital=hospital)
            lower_admins = []
            higher_admins = []
            for admin in admins:
                if admin.id < request.user.my_admin.first().id:
                    higher_admins.append([admin, admin.my_account])
                elif admin.id > request.user.my_admin.first().id:
                    lower_admins.append([admin, admin.my_account])
            if len(lower_admins)+len(higher_admins) == 0:
                return render(request, "hospital_hub/Admin/view_admins.html", {
                    "hospital_name": hospital.name,
                    "message": "Couldn't remove this admin",

                    "empty": "No other admins exists"
                })
            return render(request, "hospital_hub/Admin/view_admins.html", {
                "hospital_name": hospital.name,
                "lower_admins": lower_admins,
                "higher_admins": higher_admins,
                "message": "Couldn't remove this admin"
            })

    def RemoveSpeciality(request, speciality_id):
        specialityset = Speciality.objects.filter(id=speciality_id)
        if specialityset.count() == 1:
            speciality = specialityset.first()
            request.user.my_admin.first().hospital.specialities.remove(speciality)
            doctors = DoctorModel.objects.filter(
                hospital=request.user.my_admin.first().hospital, speciality=speciality)
            for doctor in doctors:
                doctor.is_employed = False
                doctor.hospital = None
                for schedule in doctor.dailyschedule.all():
                    schedule.delete()
                doctor.save()
        return HttpResponseRedirect(reverse('view_specialities'))

    def RemoveDoctorFromSpeciality(request, doctor_id):
        doctorset = DoctorModel.objects.filter(id=doctor_id)
        if doctorset.count() == 1:
            doctor = doctorset.first()
            doctor.is_employed = False
            doctor.hospital = None
            for schedule in doctor.dailyschedule.all():
                schedule.delete()
            doctor.save()
        return HttpResponseRedirect(reverse('view_speciality', kwargs={'speciality': doctor.speciality}))

    def RemoveDoctorFromDoctors(request, doctor_id):
        doctorset = DoctorModel.objects.filter(id=doctor_id)
        if doctorset.count() == 1:
            doctor = doctorset.first()
            doctor.is_employed = False
            doctor.hospital = None
            for schedule in doctor.dailyschedule.all():
                schedule.delete()
            doctor.save()
        return HttpResponseRedirect(reverse('admin_view_doctors'))

############################################################################
# Doctor app


class Doctor:
    def DoctorRegister(request):
        cities = CityModel.objects.all()
        specialities = SpecialityModel.objects.all()

        if request.method == "POST":
            username = request.POST["username"]
            full_name = request.POST["full_name"]
            email = request.POST["email"]
            city = request.POST["city"]
            phone_number = request.POST["phone_number"]
            speciality = request.POST["speciality"]
            password = request.POST["password"]
            confirm_password = request.POST["confirm_password"]
            if password != confirm_password:
                return render(request, "hospital_hub/Doctor/doctor_register.html", {
                    "message": "Passwords must match.",
                    "cities": cities,
                    "specialities": specialities,
                })
            image = request.FILES.get('image', None)
            print(image)
            # Atempt to create new user
            try:
                selectedCity = CityModel.objects.filter(id=city).first()
                selectedSpeciality = SpecialityModel.objects.filter(
                    id=speciality).first()

                if image is not None:
                    user = User.objects.create_user(username=username, email=email, full_name=full_name,
                                                    password=password, is_doctor=True, city=selectedCity, phone_number=phone_number, image=image)
                else:
                    user = User.objects.create_user(username=username, email=email, full_name=full_name,
                                                    password=password, is_doctor=True, city=selectedCity, phone_number=phone_number)
                doctor = DoctorModel(my_account=user,
                                     speciality=selectedSpeciality)
                user.save()
                doctor.save()
            except IntegrityError:
                return render(request, "hospital_hub/Doctor/doctor_register.html", {
                    "message": "Doctor already exist.",
                    "cities": cities,
                    "specialities": specialities,
                })
            login(request, user)
            # why not doctor home
            return HttpResponseRedirect(reverse("doctor_home"))
        else:
            return render(request, "hospital_hub/Doctor/doctor_register.html", {
                "cities": cities,
                "specialities": specialities,
            })

    def DoctorLogin(request):
        # redirect users to home page if they are already signed in as patients
        if request.user.is_authenticated:  # if already signed in
            if request.user.is_doctor:
                return HttpResponseRedirect(reverse('doctor_home'))

        if request.method == 'POST':
            username = request.POST.get("doctor_username", None)
            password = request.POST.get("doctor_password", None)
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_doctor:
                    login(request, user)
                    return HttpResponseRedirect(reverse("doctor_home"))
                else:
                    return render(request, "hospital_hub\login.html", {
                        "message": "Invalid username or password",
                        "radio": "doctor"
                    })
            else:
                return render(request, "hospital_hub\login.html", {
                    "message": "Invalid username or password",
                    "radio": "doctor"
                })
        else:
            return render(request, "hospital_hub\login.html", {
                "radio": "doctor"
            })

    def DoctorHome(request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('doctor_login'))
        elif not request.user.is_doctor:
            logout(request)
            return HttpResponseRedirect(reverse('doctor_login'))

        doctor = DoctorModel.objects.filter(my_account=request.user).first()
        schedule = Schedule.objects.filter(doctor=doctor).first()
        appointment = Appointment.objects.filter(
            schedule=schedule, appt_date=datetime.today()).all()
        status = Appointment.objects.filter(status=pending).first()
        # give all pending any day for the doctor
        pending = Appointment.objects.filter(
            schedule=schedule, status=status).all()

        return render(request, "hospital_hub/Doctor/doctor_homepage.html", {
            "doctor": doctor,
            "apointments": appointment,
            "pending": pending,
        })

    def DoctorSchedule(request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('doctor_login'))
        elif not request.user.is_doctor:
            logout(request)
            return HttpResponseRedirect(reverse('doctor_login'))

        doctor = DoctorModel.objects.filter(my_account=request.user).first()
        schedule = Schedule.objects.filter(doctor=doctor).first()
        next_month_schedule = []
        day = datetime.today()

        for i in range(7):
            day = day + datetime.timedelta(1)
            appointments = Appointment.objects.filter(
                schedule=schedule, appt_date=day.date()).all()
            next_month_schedule.append(appointments)

        return render(request, "hospital_hub/Doctor/doctor_homepage.html", {
            "doctor": doctor,
            "next_month_schedule": next_month_schedule,
        })

    def DoctorViewRecord(request, appointment):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('doctor_login'))
        elif not request.user.is_doctor:
            logout(request)
            return HttpResponseRedirect(reverse('doctor_login'))

        patient = appointment.patient
        doctor = DoctorModel.objects.filter(my_account=request.user).first()
        appointments = Appointment.objects.filter(patient=patient).all()
        docs = []
        tests = []
        if request == "POST":
            title = request.POST["title"]
            attachment = request.POST["attachment"]
            diagnosis = request.POST["diagnosis"]
            disease = request.POST["disease"]

        for apt in appointments:
            doc = AppointmentDocument.objects.filter(Appointment=apt)
            docs.append(doc)
            tests.append(MedicalTest.objects.filter(doc))

        return render(request, "hospital_hub/Doctor/doctor_homepage.html", {
            "patient": patient,
            "doctor": doctor,
            "documents": docs,  # array
            "tests": tests,  # array
        })

    def DoctorLogout(request):
        logout(request)
        return HttpResponseRedirect(reverse('doctor_login'))


############################################################################
# patient app
class Patient:

    def PatientRegister(request):
        cities = CityModel.objects.all()

        if request.method == "POST":
            username = request.POST["username"]
            full_name = request.POST["full_name"]
            email = request.POST["email"]
            password = request.POST["password"]
            confirm_password = request.POST["confirm_password"]
            city = request.POST["city"]
            phone_number = request.POST["phone_number"]
            image = request.FILES.get('image', None)

            if password != confirm_password:
                return render(request, "hospital_hub/Patient/patient_register.html", {
                    "message": "Passwords must match.",
                    "cities": cities,
                    "full_name": full_name,
                    "cities": cities,
                    "city": city,
                    "username": username,
                    "email": email,
                    "phone_number": phone_number})

        # Attempt to create new user
            try:
                selectedCity = CityModel.objects.filter(id=city).first()

                if image is not None:
                    user = User.objects.create_user(username, email, full_name,
                                                    password, is_patient=True, city=selectedCity, phone_number=phone_number, image=image)
                else:
                    user = User.objects.create_user(username, email, full_name,
                                                    password, is_patient=True, city=selectedCity, phone_number=phone_number)

                user.save()
                patient = PatientModel(my_account=user)
                patient.save()

            except IntegrityError:
                return render(request, "hospital_hub/Patient/patient_register.html", {
                    "message": "Username or Email already taken.",
                    "full_name": full_name,
                    "cities": cities,
                    "city": city,
                    "phone_number": phone_number,
                    "username": username,
                    "email": email

                })
            login(request, user)  # Checks authentication
            return HttpResponseRedirect(reverse("patient_home"))
        else:
            return render(request,
                          "hospital_hub/Patient/patient_register.html", {
                              "cities": cities,
                          })

    def PatientHome(request):
        # Redirect PATIENTS to login page if they are not signed in as admins
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        elif not request.user.is_patient:
            # may add later "you have no access to this page :( "
            logout(request)
            return HttpResponseRedirect(reverse('patient_home'))

        allspecialities = SpecialityModel.objects.all()
        allhospitals = HospitalModel.objects.all()
        alldoctors = DoctorModel.objects.filter(is_employed=True)
        doclist = []
        for doc in alldoctors:
            doclist.append(doc.my_account)

        if request.method == "POST":
            search_item = request.POST['search_item']
            resspecialities = SpecialityModel.objects.filter(
                name__contains=search_item)
            reshospitals = HospitalModel.objects.filter(
                name__contains=search_item)
            resdoctors = User.objects.filter(
                full_name__contains=search_item, doctor=True)
            docacclist = []

            for doc in resdoctors:
                if doc.my_doctor.first().is_employed:
                    docacclist.append([doc.my_doctor.first(), doc])

            if resspecialities.count()+reshospitals.count()+resdoctors.count() == 0:
                return render(request, "hospital_hub/Patient/search_results.html", {
                    "search_key": search_item,
                    "message": "No results found",
                    "allspecialities": allspecialities,
                    "allhospitals": allhospitals,
                    "alldoctors": doclist
                })
            else:
                return render(request, "hospital_hub/Patient/search_results.html", {
                    "search_key": search_item,
                    "allspecialities": allspecialities,
                    "allhospitals": allhospitals,
                    "alldoctors": doclist,
                    "specialities": resspecialities,
                    "hospitals": reshospitals,
                    "doctors": docacclist
                })

        return render(request, "hospital_hub/Patient/patient_home.html", {
            "allspecialities": allspecialities,
            "allhospitals": allhospitals,
            "alldoctors": doclist
        })

    def PatientLogin(request):
        # redirect users to home page if they are already signed in as patients
        if request.user.is_authenticated:  # if already signed in
            if request.user.is_patient:
                return HttpResponseRedirect(reverse('patient_home'))

        if request.method == "POST":
            # attempt to sign user in
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)

            # check if authentication successful
            if user is not None:
                # check if the user is patient
                if user.is_patient:
                    login(request, user)
                    return HttpResponseRedirect(reverse("patient_home"))
                else:
                    return render(request, "hospital_hub/Patient/patient_login.html", {
                        "message": "invald username or password",
                        "submitted_username": username,
                    })
            else:
                return render(request, "hospital_hub/Patient/patient_login.html", {
                    "message": "invald username or password",
                    "submitted_username": username,
                })
        else:
            return render(request, "hospital_hub/Patient/patient_login.html")

    def patientlogout(request):
        logout(request)
        return HttpResponseRedirect(reverse('login'))

    def searchbyspeciality(request):
        if request.method == "POST":
            # assuming key of the search bar is search_here
            search_item = request.POST["search_item"]
            regex = '^[a-zA-Z ]+$'  # accept these symbols

            print('search by specialities')
            if re.findall(regex, search_item):
                # it is a valid search string
                specialities = SpecialityModel.objects.filter(
                    name__contains=search_item)
                logging.debug(specialities)
                if len(specialities) == 0:
                    return render(request, "hospital_hub/Patient/searchbyspeciality.html", {
                        "message": "No results found"
                    })
            else:
                return render(request, "hospital_hub/Patient/searchbyspeciality.html", {
                    "message": "Invalid characters"
                })

        return render(request, "hospital_hub/Patient/searchbyspeciality.html")

    def find_hospitals_by_speciality(request):
        if request.method == "POST":
            # assuming key of the search bar is search_here
            speciality = request.POST["speciality"]

            print('hospital search')
            # it is a valid search string
            """ hospitals=HospitalModel.objects.filter(specialities__in=speciality) """
            hospitals = HospitalModel.objects.filter(specialities__in=[])
            logging.debug(hospitals)
            if len(hospitals) == 0:
                return render(request, "hospital_hub/Patient/hospitals_by_speciality.html", {
                    "message": "No results found"
                })

        return render(request, "hospital_hub/Patient/hospitals_by_speciality.html")
