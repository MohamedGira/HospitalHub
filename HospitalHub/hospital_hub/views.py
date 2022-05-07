from datetime import datetime
from email import message
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
from .models import Schedule as ScheduleModel
from .models import Appointment as AppointmentModel
from .models import AppointmentDocument as AppointmentDocsModel
from .utils import *
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import re
import datetime
##
from django.contrib import messages
##
import logging

logging.basicConfig(level=logging.DEBUG)

User = get_user_model()
# Create your views here.


def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


def index(request):
    if not request.user.is_authenticated:
        return render(request, "hospital_hub/index.html")
    else:
        if request.user.is_admin:
            return HttpResponseRedirect(reverse('admin_home'))
        elif request.user.is_patient:
            return HttpResponseRedirect(reverse('patient_home'))
        elif request.user.is_doctor:
            Logout(request)

    return render(request, "hospital_hub/index.html")


def Login(request):
    # redirect users to home page if they are already signed in as patients
    if request.user.is_authenticated:  # if already signed in
        if request.user.is_doctor:
            return HttpResponseRedirect(reverse('doctor_dashboard'))
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
                    return HttpResponseRedirect(reverse("doctor_dashboard"))
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


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead < 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


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
            if user is not None:
                # Check if owner is user
                if user.is_owner:
                    login(request, user)
                    return HttpResponseRedirect(reverse("owner_home"))
                else:
                    return render(request, "hospital_hub/owner/owner_login.html", {
                        "message": "Invalid username or password",
                        "submitted_username": username,
                    })
            else:
                return render(request, "hospital_hub/owner/owner_login.html", {
                    "message": "Invalid username or password",
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
            logout(request)
            return HttpResponseRedirect(reverse('owner_login'))
        return render(request, "hospital_hub/Owner/owner_home.html")

    def OwnerAddAdmin(request):  # register new admin to my hospital
        # Redirect users to login page if they are not signed in as owner
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

    def OwnerAddHospitals(request):  # register new  hospital
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

    def OwnerViewHospitals(request):
        # Redirect users to login page if they are not signed in as owners
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('owner_login'))
        elif not request.user.is_owner:
            return HttpResponseRedirect(reverse('home'))

        hospitals = HospitalModel.objects.all()

        if hospitals.count() == 0:
            return render(request, "hospital_hub/Owner/owner_view_hospitals.html", {"hospitals": None})
        else:
            return render(request, "hospital_hub/Owner/owner_view_hospitals.html", {"hospitals": hospitals})

    def OwnerViewSpecialities(request, hospital_id):
        # Redirect users to login page if they are not signed in as owners
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('owner_login'))
        elif not request.user.is_owner:
            return HttpResponseRedirect(reverse('home'))

        hospitalset = Hospital.objects.filter(id=hospital_id)
        if hospitalset.count() == 1:
            hospital = hospitalset.first()
            specialities = hospital.specialities.all()
            if specialities.count() == 0:
                return render(request, "hospital_hub/Owner/owner_view_specialities.html", {
                    "specialities": None,
                    "hospital": hospital,
                    #   "hospital_name":hospital.name,
                })
            else:
                return render(request, "hospital_hub/Owner/owner_view_specialities.html", {
                    "specialities": specialities,
                    "hospital":  hospital,  # message: message,

                    #   "hospital_name":hospital.name,
                })
        else:
            return render(request, "hospital_hub/Owner/owner_view_hospitals.html", {
                "message": "Invalid id",
                "hospitals":  HospitalModel.objects.all(),  # message: message,

                #   "hospital_name":hospital.name,
            })

    def OwnerViewSpeciality(request, hospital_id, speciality_name):
        hospitalset = HospitalModel.objects.filter(id=hospital_id)
        if hospitalset.count() == 1:
            spec = Speciality.objects.filter(name=speciality_name)
            hospital = hospitalset.first()
            if spec.count() == 1:
                doctors = DoctorModel.objects.filter(
                    speciality=spec.first(), hospital=hospital)

                return render(request, "hospital_hub/owner/owner_view_speciality.html", {
                    "doctors": doctors,
                    "hospital_name": hospital.name,
                    "speciality": spec.first().name
                })
            else:
                specialities = hospital.specialities.all()
                return render(request, "hospital_hub/owner/owner_view_specialities.html", {
                    "message": "Requested specialitiy doesn't exist",
                    "specialities": hospital.specialities.all(),
                    "hospital":  hospital

                })
        else:
            return HttpResponseRedirect('owner_view_specialities')

    def OwnerViewDoctorProfile(request, doctor_name):

        hospital = request.user.my_admin.first().hospital
        doc_account = User.objects.filter(username=doctor_name, doctor=True)
        doctor = doc_account.first().my_doctor.first()

        if doc_account.count() == 1:
            doc = doc_account.first().my_doctor.first()
            account = doc_account.first()
            reviews = doc.my_reviews.all()
            reviews_left = []
            reviews_right = []

            schedules = doc.dailyschedule.all()
            schedule_abbreviation = []

            total_reviews = 0
            for i in range(reviews.count()):
                total_reviews += reviews[i].rating
                if i <= reviews.count()/2:
                    reviews_left.append(reviews[i])
                else:
                    reviews_right.append(reviews[i])
            if reviews.count():
                total_reviews = int(total_reviews/reviews.count())

            for schedule in schedules:
                schedule_abbreviation.append([schedule, schedule.day[0:3]])

            return render(request, "hospital_hub/owner/owner_view_doctor_profile.html", {
                "doctor": doc,
                "account": account,
                "hospital": hospital,
                "schedules": schedule_abbreviation,
                "reviews": reviews,
                "reviews_left": reviews_left,
                "reviews_right": reviews_right,
                "total_reviews": total_reviews,
            })

        else:
            specialities = hospital.specialities.all()
            return render(request, "hospital_hub/owner/owner_view_specialities.html", {
                "message": "Requested specialitiy doesn't exist",
                "specialities": hospital.specialities.all(),
                "hospital":  hospital

            })

   

    def RemoveHospital(request, hospital_id):
        hospitalset = HospitalModel.objects.filter(id=hospital_id)
        if hospitalset.count() == 1:
            hospital = hospitalset.first()
            specialities = hospital.specialities.all()
            for speciality in specialities:
                hospital.specialities.remove(speciality)
                doctors = DoctorModel.objects.filter(
                    hospital=hospital, speciality=speciality)
                for doctor in doctors:
                    doctor.is_employed = False
                    doctor.hospital = None
                    for schedule in doctor.dailyschedule.all():
                        schedule.delete()
                    doctor.save()
            admins = AdminModel.objects.filter(hospital=hospital)
            for admin in admins:
                if not admin.my_account.is_staff:
                    admin.my_account.delete()
                else:
                    admin.hospital = None

            hospital.delete()
            return HttpResponseRedirect(reverse('owner_view_hospitals'))
        else:
            return HttpResponseRedirect(reverse('owner_view_hospitals')+'?message=Could\'t remove hospital with such id.')


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
                hospital=hospital, speciality=speciality , is_employed=True)
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
                speciality=spec.first(), hospital=hospital, is_employed=True)
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
        days = ['Saturday', 'Sunday', 'Monday',
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
            reviews_left = []
            reviews_right = []

            total_reviews = 0
            for i in range(reviews.count()):
                total_reviews += reviews[i].rating
                if i <= reviews.count()/2:
                    reviews_left.append(reviews[i])
                else:
                    reviews_right.append(reviews[i])
            if reviews.count():
                total_reviews = int(total_reviews/reviews.count())

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
                "reviews_left": reviews_left,
                "reviews_right": reviews_right,
                "total_reviews": total_reviews,
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
        doctors = DoctorModel.objects.filter(hospital=hospital, is_employed=True)
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
        days = ['Saturday', 'Sunday', 'Monday',
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
                        is_employed=False,is_notified=False, speciality=speciality.first())
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

                
                
           

                for s in weekly_schedule:
                    s.save()

                doctor.is_notified=True 
                doctor.hospital = request.user.my_admin.first().hospital
                doctor.save()
                    
                hospital = request.user.my_admin.first().hospital
                specialities = hospital.specialities.all()
                specialities_with_doctors_dependet = []
                for speciality in specialities:
                     doctors = DoctorModel.objects.filter(
                     hospital=hospital, speciality=speciality , is_employed=True)
                     specialities_with_doctors_dependet.append([speciality, doctors])
                return render(request, "hospital_hub/Admin/view_specialities.html", {
                 "message": "A notification is sent to doctor "+ userset.first().full_name,
                "specialities": specialities_with_doctors_dependet,
                "hospital_name": request.user.my_admin.first().hospital.name,

                #   "hospital_name":hospital.name,
                 })
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
                return HttpResponseRedirect(reverse('doctor_dashboard'))

        if request.method == 'POST':
            username = request.POST.get("doctor_username", None)
            password = request.POST.get("doctor_password", None)
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_doctor:
                    login(request, user)
                    return HttpResponseRedirect(reverse("doctor_dashboard"))
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

    def DoctorDashboard(request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        elif not request.user.is_doctor:
            logout(request)
            return HttpResponseRedirect(reverse('login'))
        status_booked = AppointmentStatus.objects.get(status="booked")
        status_pending = AppointmentStatus.objects.get(status="pending")
        status_done = AppointmentStatus.objects.get(status="done")

        print(status_booked)
        print(status_pending)
        doctor = DoctorModel.objects.filter(my_account=request.user).first()
        #schedule = Schedule.objects.filter(doctor=doctor).first()
        appointmentpart1 = Appointment.objects.filter(
            doctor=doctor, appt_date=datetime.datetime.today(), status=None).all()
        appointmentpart2 = Appointment.objects.filter(
            doctor=doctor, appt_date=datetime.datetime.today(), status=status_booked).all()
        appointment=appointmentpart1|appointmentpart2
        # give all pending any day for the doctor
        pending = Appointment.objects.filter(
            doctor=doctor, status=status_pending).all()
        done = Appointment.objects.filter(
            doctor=doctor, status=status_done).all()
        # status=status
        return render(request, "hospital_hub/Doctor/doctor_dashboard.html", {
            "doctor": doctor,
            "appointments": appointment,
            "pending": pending,
            "done":done,
            "is_notified":doctor.is_notified
        })

    def DoctorProfile(request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        elif not request.user.is_doctor:
            logout(request)
            return HttpResponseRedirect(reverse('login'))

        doc_account = request.user
        doctor = DoctorModel.objects.filter(my_account=request.user).first()
        days = [ 'Monday',
                'Tuesday', 'Wednesday', 'Thursday', 'Friday','Saturday', 'Sunday']
        hospital = doctor.hospital
        reviews = doctor.my_reviews.all()
        schedules = doctor.dailyschedule.all()
        schedule_abbreviation = []

        total_reviews = 0
        reviews_left = []
        reviews_right = []
        for i in range(reviews.count()):
            print(reviews.count())
            total_reviews += reviews[i].rating
            if i <= reviews.count()/2:
                reviews_left.append(reviews[i])
            else:
                reviews_right.append(reviews[i])

        if reviews.count():
            total_reviews = int(total_reviews/reviews.count())


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

        if request.method == "POST":
            pass
        else:
            return render(request, "hospital_hub/Doctor/doctor_profile.html", {
                "doctor": doctor,
                "hospital": hospital,
                "schedules": schedule_abbreviation,
                "reviews": reviews,
                "reviews_left":reviews_left,
                "reviews_right":reviews_right,
                "total_reviews":total_reviews,
                
            })

    # def DoctorSchedule(request):
    #    if not request.user.is_authenticated:
    #        return HttpResponseRedirect(reverse('doctor_login'))
    #    elif not request.user.is_doctor:
    #        logout(request)
    #        return HttpResponseRedirect(reverse('doctor_login'))

    #    doctor = DoctorModel.objects.filter(my_account=request.user).first()
    #    schedule = Schedule.objects.filter(doctor=doctor).first()
    #    next_month_schedule = []
    #    day = datetime.today()

    #    for i in range(7):
    #        day = day + datetime.timedelta(1)
    #        appointments = Appointment.objects.filter(
    #            schedule=schedule, appt_date=day.date()).all()
    #        next_month_schedule.append(appointments)

    #    return render(request, "hospital_hub/Doctor/doctor_home.html", {
    #        "doctor": doctor,
    #        "next_month_schedule": next_month_schedule,
    #    })

    def DoctorViewRecord(request, patient_name):
        print("view")
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        elif not request.user.is_doctor:
            logout(request)
            return HttpResponseRedirect(reverse('login'))

        status_done    = AppointmentStatus.objects.get(status="done")
        status_pending = AppointmentStatus.objects.get(status="pending")
        status_booked  = AppointmentStatus.objects.get(status="booked")
        tests_list     = MedicalTestType.objects.all()
        patient_user = User.objects.filter(username=patient_name).first()
        patient = PatientModel.objects.filter(my_account=patient_user).first()

        doctor = DoctorModel.objects.filter(my_account=request.user).first()

        this_appointment = Appointment.objects.filter(
            doctor=doctor, patient=patient, appt_date=datetime.datetime.today()).first()
        is_new =False;
        if this_appointment is not None:
            if this_appointment.status==status_booked or this_appointment.status==None:
                is_new=True
        

        appointments = Appointment.objects.filter(patient=patient)
        docs_with_tests = []
        
        for apt in appointments:
            document = apt.document.first();
            if document != None:
                test = document.tests.all().first()
                docs_with_tests.append([document,test])

        if request.method == "POST":
            title = request.POST["title"]
            attachment = request.FILES.get('attachment', None)
            diagnosis = request.POST["diagnosis"]
            disease = request.POST["title"]
            reqired_test=request.POST["reqired_test"]
            try:
                doc = AppointmentDocsModel(appointment=this_appointment, title=title,
                                           attachment=attachment, diagnosis=diagnosis, disease=disease)

                if reqired_test == "None":
                    this_appointment.status = status_done
                else:
                    this_appointment.status = status_pending
                    typeset=MedicalTestType.objects.filter(type=reqired_test)
                    if typeset.count()==1:
                        test=MedicalTest(appointment_document=doc,type=typeset.first())
                        doc.save()
                        test.save()
                    else:
                        new_type=MedicalTestType(type=reqired_test)
                        new_type.save()
                        test=MedicalTest(appointment_document=doc,type=typeset.first())
                        doc.save()
                        test.save()
                        
                this_appointment.save()
                print("saved")
                doc.save()
            except IntegrityError:
                return render(request, "hospital_hub/Doctor/doctor_viewRecord.html", {
                    "message":"an Error Happened, Try again",
                    "is_new": is_new,
                    "patient": patient_user,
                    "doctor": doctor,
                    "documents": docs_with_tests,
                    "test_types":tests_list,
                })
            return HttpResponseRedirect(reverse('doctor_viewRecord',args=[patient_name]))

        return render(request, "hospital_hub/Doctor/doctor_viewRecord.html", {
            "is_new": is_new,
            "patient": patient_user,
            "doctor": doctor,
            "documents": docs_with_tests,
            "test_types":tests_list,
        })

    def DoctorLogout(request):
        logout(request)
        return HttpResponseRedirect(reverse('login'))
    
    def DoctorAccept(request, doctor_name):
         print("Confirmed")
         #Unnecesarry
         #if not request.user.is_authenticated:
         #      return render(request, "hospital_hub\login-general.html", {
         #               "message": "sign in then re-click the link",
         #               "radio": "doctor"
         #           })
         #if not request.user.is_doctor:
         #   logout(request)
         #   return render(request, "hospital_hub\login-general.html", {
         #               "message": "sign in then re-click the link",
         #               "radio": "doctor"
         #           })

         #if not request.user.username == doctor_name:
         #   logout(request)
         #   return render(request, "hospital_hub\login-general.html", {
         #               "message": "sign in then re-click the link",
         #               "radio": "doctor"
         #           })
         doctorset=User.objects.filter(username=doctor_name)

         if doctorset.count()==1:
             doctoracc=doctorset.first()
             doctor=doctoracc.my_doctor.first()
             doctor.is_employed = True
             doctor.is_notified = False
             doctor.save()
             
             #email=EmailMessage(
             #       'Employment Request To '+doctor.full_name+' is Accepted',
             #        'Doctor '+doctor.full_name+' has accepted your Employment, you can now view and edit his scedule',
             #        settings.EMAIL_USER_HOST,
             #        [admin_email],
             #        )
             #email.fail_silently=False
             #email.send()
             
             return HttpResponseRedirect(reverse('doctor_dashboard'))
             
         else:
             return HttpResponse("something went wrong")
        
    def DoctorReject(request,doctor_name):
        print("deleted")
        doctorset=User.objects.filter(username=doctor_name)
        if doctorset.count()==1:
             doctoracc=doctorset.first()
             doctor=doctoracc.my_doctor.first()
             doctor.hospital= None
             doctor.is_employed = False
             doctor.is_notified = False
             schedules=ScheduleModel.objects.filter(doctor=doctor)
             for schedule in schedules:
                 schedule.delete()
             doctor.save()
             #email=EmailMessage(
             #       'Employment Request To '+doctor.full_name+' is Rejected',
             #        'Doctor '+doctor.full_name+' has accepted your Employment.',
             #        settings.EMAIL_USER_HOST,
             #        [admin_email],
             #        )
             #email.fail_silently=False
             #email.send()
             return HttpResponseRedirect(reverse('doctor_dashboard'))
        else:
             return HttpResponse("something went wrong")


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
            age= request.POST["age"]
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
                    "phone_number": phone_number,
                    "age":age
                    })

        # Attempt to create new user
            try:
                selectedCity = CityModel.objects.filter(id=city).first()

                if image is not None:
                    user = User.objects.create_user(username, email, full_name,
                                                    password, is_patient=True, city=selectedCity, phone_number=phone_number, image=image,age=age)
                else:
                    user = User.objects.create_user(username, email, full_name,
                                                    password, is_patient=True, city=selectedCity, phone_number=phone_number,age=age)

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
                    "email": email,
                    "age":age

                })
            login(request, user)  # Checks authentication
            return HttpResponseRedirect(reverse("patient_home"))
        else:
            return render(request,
                          "hospital_hub/Patient/patient_register.html", {
                              "cities": cities,
                          })

    def PatientHome(request):
        #####consider making patient and anonymous user have the same functionalitis(except in booking and commenting)######

       # Redirect PATIENTS to login page if they are not signed in as patient

        # if not request.user.is_authenticated:
        #    return HttpResponseRedirect(reverse('login'))
        # if not request.user.is_patient:
        #    # may add later "you have no access to this page :( "
        #    logout(request)
        #    return HttpResponseRedirect(reverse('patient_home'))

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

    def ViewDoctorProfile(request, doctor_name):

        doc_account = User.objects.filter(username=doctor_name, doctor=True)
        if doc_account.count() == 1:
            doctor = doc_account.first().my_doctor.first()
            hospital = doctor.hospital
            reviews = doctor .my_reviews.all()
            schedules = doctor .dailyschedule.all()
            schedule_abbreviation_days = []
            patient_account = User.objects.filter(
                username=request.user.username, patient=True).first()

            total_reviews = 0
            reviews_left = []
            reviews_right = []
            for i in range(reviews.count()):
                print(reviews.count())
                total_reviews += reviews[i].rating
                if i <= reviews.count()/2:
                    reviews_left.append(reviews[i])
                else:
                    reviews_right.append(reviews[i])
            if reviews.count():
                total_reviews = int(total_reviews/reviews.count())
 

            days = ['Monday', 'Tuesday', 'Wednesday',
                    'Thursday', 'Friday', 'Saturday', 'Sunday']

            for schedule in schedules:
                nextday = next_weekday(
                    datetime.datetime.today(), days.index(schedule.day))
                next_month_dates_waiting = []
                patients_ahead = AppointmentModel.objects.filter(
                    doctor=doctor, appt_date=nextday.date()).count()
                next_month_dates_waiting.append([nextday, patients_ahead])
                for j in range(3):
                    nextday = nextday + datetime.timedelta(7)
                    patients_ahead = AppointmentModel.objects.filter(
                        doctor=doctor, appt_date=nextday.date()).count()
                    next_month_dates_waiting.append([nextday, patients_ahead])

                schedule_abbreviation_days.append(
                    [[schedule, schedule.day[0:3]], next_month_dates_waiting])

            if request.method == "POST":
                if request.POST['command'] == "confirm":
                    if patient_account is None:
                        return render(request, "hospital_hub/Patient/book_appointment.html", {
                            "message": "You have to sign in to book",
                            "doctor": doctor,
                            "account": doc_account.first(),
                            "hospital": hospital,
                            "schedules": schedule_abbreviation_days,
                            "reviews": reviews,
                            "reviews_left": reviews_left,
                            "reviews_right": reviews_right,
                            "total_reviews": total_reviews,

                        })
                    else:
                        appt_date = request.POST['appt_date']
                        selected_schedule = ScheduleModel.objects.filter(
                            id=request.POST['schedule']).first()
                        appt_count = AppointmentModel.objects.filter(
                            doctor=doctor, appt_date=appt_date).count()

                        if appt_count < selected_schedule.patient_count:
                            exsiting_appointments = AppointmentModel.objects.filter(doctor=doctor,
                                                                                    patient=patient_account.my_patient.first(),
                                                                                    appt_date=appt_date)
                            if exsiting_appointments.count() == 0:

                                patient_no = appt_count+1
                                appointment = AppointmentModel()
                                appointment.doctor = doctor
                                appointment.patient = patient_account.my_patient.first()
                                appointment.schedule = selected_schedule
                                appointment.patient_no = patient_no
                                appointment.appt_date = appt_date
                                # appointment.status=AppointmentStatus.objects.filter("Booked").first()
                                appointment.save()
                                return HttpResponseRedirect(reverse('book_appointment', args=[doctor_name]))
                            else:
                                return render(request, "hospital_hub/Patient/book_appointment.html", {
                                    "message": "you already have an appointment on this day, your turn is ("
                                    + str(exsiting_appointments.first().patient_no)+").",
                                    "doctor": doctor,
                                    "account": doc_account.first(),
                                    "hospital": hospital,
                                    "schedules": schedule_abbreviation_days,
                                    "reviews": reviews,
                                    "reviews_left": reviews_left,
                                    "reviews_right": reviews_right,
                                    "total_reviews": total_reviews,
                                })

                        else:
                            return render(request, "hospital_hub/Patient/book_appointment.html", {
                                "message": "No available appointments on this day.",
                                "doctor": doctor,
                                "account": doc_account.first(),
                                "hospital": hospital,
                                "schedules": schedule_abbreviation_days,
                                "reviews": reviews,
                                "reviews_left": reviews_left,
                                "reviews_right": reviews_right,
                                "total_reviews": total_reviews,
                            })
                elif request.POST['command'] == "add_rating":
                    rating = 3
                    if request.POST.get('rating', False):
                        rating = request.POST['rating']
                        comment = request.POST['comment']
                        if AppointmentModel.objects.filter(doctor=doctor, patient=patient_account.my_patient.first()).count() > 0:
                            review = Review(doctor=doctor, patient=patient_account.my_patient.first(
                            ), rating=rating, comment=comment)
                            review.save()
                        else:
                            return render(request, "hospital_hub/Patient/book_appointment.html", {
                                "message": "You had no appointments with this doctor, you can't add rating.",
                                "doctor": doctor,
                                "account": doc_account.first(),
                                "hospital": hospital,
                                "schedules": schedule_abbreviation_days,
                                "reviews": reviews,
                                "reviews_left": reviews_left,
                                "reviews_right": reviews_right,
                                "total_reviews": total_reviews, })

                    return HttpResponseRedirect(reverse('book_appointment', args=[doctor_name]))
                else:
                    return HttpResponseRedirect(reverse('book_appointment', args=[doctor_name]))

            return render(request, "hospital_hub/Patient/book_appointment.html", {
                "doctor": doctor,
                "account": doc_account.first(),
                "hospital": hospital,
                "schedules": schedule_abbreviation_days,
                "reviews": reviews,
                "reviews_left": reviews_left,
                "reviews_right": reviews_right,
                "total_reviews": total_reviews,
            })

        else:
            specialities = Speciality.objects.all()
            return render(request, "hospital_hub/Patient/view_specialities.html", {
                "message": "No doctor by this name exitsts in your hospital.",
                "specialities": specialities,
            })

    def ViewDoctors(request):
        doctors = DoctorModel.objects.filter(is_employed=True)

        return render(request, "hospital_hub/Patient/view_doctors.html", {
            "doctors": doctors
        })

    def ViewSpecialities(request):
        # Redirect users to login page if they are not signed in as admins

        specialities = SpecialityModel.objects.all()

        if specialities.count() == 0:
            return render(request, "hospital_hub/Patient/view_specialities.html", {
                "specialities": None,
            })
        else:
            return render(request, "hospital_hub/Patient/view_specialities.html", {
                "specialities": specialities,
            })

    def ViewAppointments(request):
        if request.method == "GET":
            user = User.objects.filter(
                username=request.user.username, patient=True).first()
            patient = PatientModel.objects.filter(my_account=user).first()

            print("appt_patient")
            print(patient)
            # it is a valid search string
            appointments = AppointmentModel.objects.filter(patient=patient.id)
            print(appointments)
            if len(appointments) == 0:
                return render(request, "hospital_hub/Patient/view_appointments.html", {
                    "message": "No results found"
                })

            return render(request, "hospital_hub/Patient/view_appointments.html", {
                "appointments": appointments
            })

    def ViewAppointmentDocs(request, appt_id):
        if request.method == "GET":
            user = User.objects.filter(
                username=request.user.username, patient=True).first()
            patient = PatientModel.objects.filter(my_account=user).first()

            appointmentDocs = AppointmentDocsModel.objects.filter(
                appointment=appt_id)
            print("appt_docs")
            print(appointmentDocs)
            if len(appointmentDocs) == 0:
                return render(request, "hospital_hub/Patient/view_appointments_docs.html", {
                    "message": "No results found"
                })

            return render(request, "hospital_hub/Patient/view_appointments_docs.html", {
                "appointmentDocs": appointmentDocs
            })

    def PatientViewHospital(request, hospital_id):

        hospitalset = Hospital.objects.filter(id=hospital_id)
        if hospitalset.count() == 1:
            hospital = hospitalset.first()
            specialities = hospital.specialities.all()
            if specialities.count() == 0:
                return render(request, "hospital_hub/Patient/view_hospital.html", {
                    "specialities": None,
                    "hospital": hospital,
                    #   "hospital_name":hospital.name,
                })
            else:
                return render(request, "hospital_hub/Patient/view_hospital.html", {
                    "specialities": specialities,
                    "hospital":  hospital,  # message: message,

                    #   "hospital_name":hospital.name,
                })
        else:
            return render(request, "hospital_hub/Patient/patient_home.html", {
                "message": "Invalid id",



            })

    def PatientViewHospitalSpeciality(request, hospital_id, speciality_name):
        hospitalset = HospitalModel.objects.filter(id=hospital_id)
        if hospitalset.count() == 1:
            spec = Speciality.objects.filter(name=speciality_name)
            hospital = hospitalset.first()
            if spec.count() == 1:
                doctors = DoctorModel.objects.filter(
                    speciality=spec.first(), hospital=hospital, is_employed=True)

                return render(request, "hospital_hub/patient/patient_view_speciality.html", {
                    "doctors": doctors,
                    "hospital_name": hospital.name,
                    "speciality": spec.first().name
                })
            else:
                specialities = hospital.specialities.all()
                return render(request, "hospital_hub/patient/patient_view_speciality.html", {
                    "message": "Requested specialitiy doesn't exist",
                    "specialities": hospital.specialities.all(),
                    "hospital":  hospital

                })
        else:
            return HttpResponseRedirect('patient_home')

    def PatientViewSpeciality(request, speciality_name):
        spec = Speciality.objects.filter(name=speciality_name)
        if spec.count() == 1:
            doctors = DoctorModel.objects.filter(
                speciality=spec.first(), is_employed=True)

            return render(request, "hospital_hub/patient/patient_view_speciality.html", {
                "doctors": doctors,

                "speciality": spec.first().name
            })
        else:
            specialities = SpecialityModel.objects.all()
            return render(request, "hospital_hub/patient/view_specialities.html", {
                "message": "Requested specialitiy doesn't exist",
                "specialities": specialities,


            })

    def ViewHospitals(request):
        hospitals = HospitalModel.objects.all()

        return render(request, "hospital_hub/Patient/view_hospitals.html", {
            "hospitals": hospitals
        })
