from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.db import models
from django.conf import settings

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)

User = settings.AUTH_USER_MODEL


# all of this is used as options lists througout the app
class Speciality(models.Model):
    name =models.CharField(max_length=100,unique=True)
    url=models.TextField(null = True)
    def __str__(self):
        return self.name

class MedicalTestType(models.Model):    
    type= models.CharField(max_length=100);
    def __str__(self):
        return self.type

class City(models.Model):
    name =models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.name

class AppointmentStatus(models.Model):
    status =models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Hospital(models.Model):
    name =models.CharField(max_length=100)
    city = models.ForeignKey(City,on_delete=models.PROTECT,null=True)
    specialities = models.ManyToManyField(Speciality)
    #url = models.TextField(null =True)
    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, username, email,full_name=None,
                   password=None, is_owner=False,
                  is_admin=False, is_doctor=False,is_staff=False,
                  is_patient=False,city=None,phone_number=None):
        if not (username and password and full_name and email ):
            raise ValueError("Users must have all required data")
        
        user_obj = self.model(
            username = username,
            full_name=full_name,
            email=self.normalize_email(email),
            )
        user_obj.set_password(password) # change user password
        user_obj.owner = is_owner
        user_obj.admin = is_admin
        user_obj.doctor = is_doctor
        user_obj.patient = is_patient
        user_obj.staff  = is_staff
        user_obj.city= city
        user_obj.phone_number=phone_number
        user_obj.save(using=self._db)

        return user_obj

    #def create_staffuser(self, email,full_name=none, password=none):
    #    user = self.create_user(
    #            full_name=full_name,
    #            password=password,
    #            email=email,
    #            is_staff=true
    #    )
    #    return user

    def create_superuser(self, username,email, full_name=None, password=None,phone_number=None):
        user = self.create_user(
                username,
                full_name=full_name,
                password=password,
                email=email,
                phone_number=phone_number,
                is_owner=True,
                is_staff=True,
                is_admin=False
        )
        return user


class User(AbstractBaseUser):
    username    = models.CharField(max_length=255, unique=True)
    email       = models.EmailField(verbose_name = 'email address',max_length = 255,unique = True,)
    full_name   = models.CharField(max_length=255, blank=True, null=True)
    phone_number= models.IntegerField()
    city        = models.ForeignKey(City,on_delete=models.PROTECT,null=True)
    owner       = models.BooleanField(default= False) # can login 
    admin       = models.BooleanField(default= False) # staff user non superuser
    doctor      = models.BooleanField(default=False) # superuser 
    patient     = models.BooleanField(default=False) # superuser
    staff       = models.BooleanField(default=False) # necessary
    created_at  = models.DateTimeField(null=True)
    # confirm     = models.BooleanField(default=False)
    # confirmed_date     = models.DateTimeField(default=False)

    USERNAME_FIELD = 'username' #username
    EMAIL_FIELD = 'email' #Email
    # USERNAME_FIELD and password are required by default
    REQUIRED_FIELDS = ['email','full_name','phone_number']

    objects = UserManager()

    def __str__(self):
        return self.username

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.username

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_owner(self):
        return self.owner

    @property
    def is_admin(self):
        return self.admin
    
    @property
    def is_staff(self):
        return self.owner


    @property
    def is_doctor(self):
        return self.doctor

    @property
    def is_patient(self):
        return self.patient



# main users models

class Owner(models.Model):
    my_account= models.ForeignKey(User,on_delete= models.CASCADE,related_name="my_owner")
    
class Admin(models.Model):
    my_account= models.ForeignKey(User,on_delete= models.CASCADE,related_name="my_admin")
    hospital= models.ForeignKey(Hospital, on_delete=models.CASCADE,related_name="my_admins")
    def __str__(self):
        return "Hospital of "+str(self.hospital)+" - Admin "+str(self.id)

class Patient(models.Model):  
    my_account= models.ForeignKey(User,on_delete= models.CASCADE,related_name="my_patient")

class Doctor(models.Model):
    my_account= models.ForeignKey(User,on_delete= models.CASCADE,related_name="my_doctor")
    is_employed= models.BooleanField(default=False)
    speciality= models.ForeignKey(Speciality, on_delete=models.CASCADE,related_name="doctors")
    hospital= models.ForeignKey(Hospital, on_delete=models.SET_NULL,related_name="my_doctors",null=True)

# Organizational classes

class Schedule(models.Model):
    day= models.CharField(max_length=50)
    doctor= models.ForeignKey(Doctor,on_delete= models.CASCADE,related_name="dailyschedule")
    start_time=models.TimeField()
    end_time=models.TimeField()
    price=models.IntegerField()
    patient_count=models.IntegerField()

class Appointment(models.Model):
    doctor=models.ForeignKey(Doctor,on_delete= models.CASCADE,related_name="appointments")
    patient=models.ForeignKey(Patient,on_delete= models.CASCADE,related_name="appointments")
    schedule=models.ForeignKey(Schedule,on_delete= models.CASCADE,related_name="appointments")
    status=models.ForeignKey(AppointmentStatus, on_delete=models.CASCADE)
    patient_no=models.IntegerField()
    appt_date=models.DateTimeField()

class AppointmentDocument(models.Model):
    appointment= models.ForeignKey(Appointment,on_delete= models.CASCADE,related_name="document")
    title=models.CharField(max_length=100)
    attachment=models.TextField()
    diagnosis =models.TextField()
    disease=models.CharField(max_length=100)

class MedicalTest(models.Model):
    type= models.ForeignKey(MedicalTestType,on_delete= models.CASCADE,related_name="document")
    appointment_document=models.ForeignKey(AppointmentDocument,on_delete= models.CASCADE,related_name="tests")
    result=models.TextField(null=True)


class Rating(models.IntegerChoices):
    EXCELLENT = 5, '5';    VERYGOOD = 4, '4';    GOOD = 3, '3';    OK = 2, '2';BAD = 1, '1'




class Review(models.Model):
    doctor= models.ForeignKey(Doctor,on_delete= models.CASCADE,related_name="my_reviews")
    patient=models.ForeignKey(Patient,on_delete= models.CASCADE,related_name="my_comments")
    comment=models.TextField()
    rating= models.IntegerField(default=Rating.EXCELLENT, choices=Rating.choices)
