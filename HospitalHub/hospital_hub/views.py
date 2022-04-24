from django.shortcuts import render
from django.urls import reverse


# Create your views here.

def index(request):
     return render(request, "hospital_hub/index.html")




############################################################################
#owner app























############################################################################
#Admin app


def AdminHome(request):
     return render(request, "hospital_hub/Admin/hospital_admin_home.html")
































############################################################################
#Doctor app





































############################################################################
#patient app
