from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model

from .models import *

User= get_user_model()
# Create your views here.
def index(request):
     return render(request, "hospital_hub/index.html")



############################################################################
#owner app























############################################################################
#Admin app

def AdminLogin(request):
    if request.method=="POST":
        pass
    else:
        pass
    return render(request, "hospital_hub/Admin/login_admin.html")

def AdminHome(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admin_login'))
    elif not request.user.is_admin:
        return HttpResponseRedirect(reverse('admin_login'))
    return render(request, "hospital_hub/Admin/admin_home.html")
































############################################################################
#Doctor app





































############################################################################
#patient app
