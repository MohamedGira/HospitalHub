from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from .models import Patient as PatientModel
from .models import *
from .models import Admin as AdminModel
from .utils import *

User= get_user_model()
# Create your views here.
def index(request):
     return render(request, "hospital_hub/index.html")



############################################################################
#owner app






















############################################################################
#Admin app

class Admin:    

    #Admin signin/signout methods__________________________________________________________________________________

    def AdminLogin(request):
        # Redirect users to home page if they are already signed in as admins
        if request.user.is_authenticated:
            if request.user.is_admin:
                return HttpResponseRedirect(reverse('admin_home'))

        if request.method=="POST":
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
                    return render(request,"hospital_hub/admin/admin_login.html",{
                        "message":"Invald username or password",
                        "submitted_username":username,
                        })   
            else:
                return render(request,"hospital_hub/Admin/admin_login.html",{
                        "message":"Invald username or password",
                        "submitted_username":username,
                        })
        else:   
            return render(request, "hospital_hub/Admin/admin_login.html")


    def AdminLogout(request):
        logout(request)
        return HttpResponseRedirect(reverse('admin_login'))

    


    #Admin main methods__________________________________________________________________________________

    def AdminHome(request): 
        # Redirect users to login page if they are not signed in as admins
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('admin_login'))
        elif not request.user.is_admin:
        #may add later "you have no access to this page :( "
            return HttpResponseRedirect(reverse('home'))
        return render(request, "hospital_hub/Admin/admin_home.html")


    def AddAdmin(request):#register new admin to my hospital
         # Redirect users to login page if they are not signed in as admins
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('admin_login'))
        elif not request.user.is_admin:
        #may add later "you have no access to this page :( "
            return HttpResponseRedirect(reverse('home'))

        cities=City.objects.all();

        if(request.method=="POST"):
            username        =request.POST["username"]
            full_name       =request.POST["full_name"]
            email           =request.POST["email"]
            password        =request.POST["password"]
            confirm_password=request.POST["confirm_password"]
            city            =request.POST["city"]
            phone_number    =request.POST["phone_number"]
            hospital        =request.user.my_admin.first().hospital ##only one admin related to this account

            if password != confirm_password:
                return render(request, "hospital_hub/admin/add_admin.html", {
                "mustmatch": "Passwords must match.",
                "username":username,
                "email":email,
                "full_name":full_name,
                "password":password,
                "cities":cities,
                "provided_city":city,
                 "phone":phone_number,
                })

            # Attempt to create new user
            try:
                cit=City.objects.get(id=city)
                user = User.objects.create_user(username, email,full_name,
                password,is_admin=True,city=cit,phone_number=phone_number)
                user.save()
                admin= AdminModel(my_account=user,hospital=hospital) #links admin toadmin object
                admin.save()
            except IntegrityError:
                return render(request,  "hospital_hub/admin/add_admin.html", {
                    "alreadyused": "Username or email are already taken.",
                    "full_name":full_name,
                    "cities":cities,
                    "city":city,
                    "phone":phone_number,
                })
            return HttpResponseRedirect(reverse("admin_home"))            
        else:
             
             return render(request,"hospital_hub/admin/add_admin.html",{
                 "cities":cities,
                 })


    def AddSpeciality(request):
        # Redirect users to login page if they are not signed in as admins
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('admin_login'))
        elif not request.user.is_admin:
        #may add later "you have no access to this page :( "
            return HttpResponseRedirect(reverse('home'))


        specialities=Speciality.objects.all()
        if request.method == "POST":
            #check if input is valid
            speciality=Speciality.objects.filter(id=request.POST["speciality"]).first()
            if speciality is not None:
                hospital=request.user.my_admin.first().hospital
                #check if hospital haven't already added this speciality
                if hospital.specialities.filter(name=speciality.name).count()==0:
                    hospital.specialities.add(speciality)
                    hospital.save()
                    return HttpResponseRedirect(reverse("admin_home"))            
                else:
                   return render(request,"hospital_hub/Admin/add_speciality.html",{
                       "specialities":specialities,
                       "provided_spec":hospital.specialities.filter(name=speciality.name).first(),
                       "message":"This speciality is already added to yout hospital"})
            else:
                   return render(request,"hospital_hub/Admin/add_speciality.html",{
                       "specialities":specialities,
                       "message":"Invalid Input"})

        return render(request,"hospital_hub/Admin/add_speciality.html",{
            "specialities":specialities,
            })
        




    def ViewSpecialities(request):
        return render(request, "hospital_hub/Admin/view_specialities.html")







############################################################################
#Doctor app





































############################################################################
#patient app
class Patient:
    
    def register(request):
        if request.method == "POST":
            username        =request.POST["username"]
            full_name       =request.POST["full_name"]
            email           =request.POST["email"]
            password        =request.POST["password"]
            confirm_password=request.POST["confirm_password"]
            city            =request.POST["city"]
            phone_number    =request.POST["phone_number"]
            if password != confirmation:
                return render(request, "hospital_hub/Patient/login.html", {
                "message": "Passwords must match." })

        # Attempt to create new user
            try:
                user = User.objects.create_user(username, email,full_name,password, 
                    is_patient=True,city=None,phone_number=phone_number)
                user.save()
            except IntegrityError:
                return render(request, "hospital_hub/Patient/patient_register.html", {
                    "message": "Username already taken."
                })
            login(request, user) #Checks authentication
            return HttpResponseRedirect(reverse("index")) 
        else:
            return render(request, "hospital_hub/Patient/patient_register.html") 



""" 
    def PatientHome(request): 
        # Redirect PATIENTS to login page if they are not signed in as admins
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('patient_login'))
        elif not request.user.is_patient:
        #may add later "you have no access to this page :( "
            return HttpResponseRedirect(reverse('home'))
        return render(request, "hospital_hub/Admin/a_home.html") """


    
 def Patientlogin(request):
       # redirect users to home page if they are already signed in as patients
       if request.user.is_authenticated:
           if request.user.is_patient:
               return httpresponseredirect(reverse('patient_home'))

       if request.method=="post":
            # attempt to sign user in
           username = request.post["username"]
           password = request.post["password"]
           user = authenticate(request, username=username, password=password)

           # check if authentication successful
           if user is not none:
               # check if the user is patient
               if user.is_patient:
                   login(request, user)
                   return httpresponseredirect(reverse("patient_home"))
               else:
                   return render(request,"hospital_hub/Patient/patient_login.html",{
                       "message":"invald username or password",
                       "submitted_username":username,
                       })   
           else:
               return render(request,"hospital_hub/Patient/patient_login.html",{
                       "message":"invald username or password",
                       "submitted_username":username,
                       })
       else:   
           return render(request, "hospital_hub/Patient/patient_login.html")


   def patientlogout(request):
       logout(request)
       return httpresponseredirect(reverse('patient_login')) 
     

#          def addadmin(request):#register new admin to my hospital
#         # redirect users to login page if they are not signed in as admins
#        if not request.user.is_authenticated:
#            return httpresponseredirect(reverse('admin_login'))
#        elif not request.user.is_admin:
#        #may add later "you have no access to this page :( "
#            return httpresponseredirect(reverse('home'))

#        cities=city.objects.all();

#        if(request.method=="post"):
#            username        =request.post["username"]
#            full_name       =request.post["full_name"]
#            email           =request.post["email"]
#            password        =request.post["password"]
#            confirm_password=request.post["confirm_password"]
#            city            =request.post["city"]
#            phone_number    =request.post["phone_number"]
#            hospital        =request.user.my_admin.first().hospital ##only one admin related to this account

#            if password != confirm_password:
#                return render(request, "hospital_hub/admin/add_admin.html", {
#                "mustmatch": "passwords must match.",
#                "username":username,
#                "email":email,
#                "full_name":full_name,
#                "password":password,
#                "cities":cities,
#                "provided_city":city,
#                 "phone":phone_number,
#                })

#            # attempt to create new user
#            try:
#                cit=city.objects.get(id=city)
#                user = user.objects.create_user(username, email,full_name,
#                password,is_admin=true,city=cit,phone_number=phone_number)
#                user.save()
#                admin= adminmodel(my_account=user,hospital=hospital) #links admin toadmin object
#                admin.save()
#            except integrityerror:
#                return render(request,  "hospital_hub/admin/add_admin.html", {
#                    "alreadyused": "username or email are already taken.",
#                    "full_name":full_name,
#                    "cities":cities,
#                    "city":city,
#                    "phone":phone_number,
#                })
#            return httpresponseredirect(reverse("admin_home"))            
#        else:
             
#             return render(request,"hospital_hub/admin/add_admin.html",{
#                 "cities":cities,
#                 })
# """
