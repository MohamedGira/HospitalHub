from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout

from .models import *

User= get_user_model()
# Create your views here.
def index(request):
     return render(request, "hospital_hub/index.html")



############################################################################
#owner app























############################################################################
#Admin app
    
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























############################################################################
#Doctor app





































############################################################################
#patient app
