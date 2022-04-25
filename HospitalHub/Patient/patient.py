from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.db import models
from django.conf import settings

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)

User = settings.AUTH_USER_MODEL

class Patient:
    
    def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        full_name = request.POST["full_name"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email,full_name,
                   password, is_owner=True,
                  is_admin=False, is_doctor=False,is_staff=False,
                  is_patient=True,city=None,phone_number)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html") 
        #gvgvgvgvgvg