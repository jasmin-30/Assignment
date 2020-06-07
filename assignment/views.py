import datetime

from django.conf import settings as st
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

from .models import *


# Create your views here.

def HomePageView(request):
    context = {
        'base_url': st.BASE_URL
    }
    if request.method == "POST":
        if request.POST.get('email_address') is not None:
            email = request.POST.get('email_address')
            pwd = request.POST.get('password')

            try:
                user_obj = User.objects.get(email=email)

            except User.DoesNotExist:
                context["error"] = "Email ID does not exist. Register first."
                return render(request, "home.html", context)

            user = authenticate(request, username=email, password=pwd)
            if user is not None:
                login(request, user)
                return HttpResponse("Logged in")

            else:
                context["error"] = "Please enter valid credentials."
                return render(request, 'home.html', context)

        if request.POST.get('email') is not None:
            fname = request.POST.get('first_name')
            lname = request.POST.get('last_name')
            email = request.POST.get('email')
            contact = request.POST.get('contact')
            dob = str(request.POST.get('dob'))
            city = request.POST.get('city')
            pwd = request.POST.get('password')

            try:
                user = User.objects.create_user(email, password=pwd)
                print(user)
            except IntegrityError as e:
                # Integrity error means email id is already registered
                print(e)
                context["error"] = "Email ID is already Registered. Log in with valid credentials."
                return render(request, "home.html", context)

            try:
                user.first_name = fname
                user.last_name = lname
                user.contact = contact
                user.city = city
                dob_list = dob.split("/")
                user.DOB = datetime.datetime(int(dob_list[2]), int(dob_list[1]), int(dob_list[0]))
                user.save()
                context["success"] = "Successfully Registered."
                return render(request, 'home.html', context)

            except Exception as e:
                print(e)
                user.delete()
                context["error"] = "Technical Error occured."
                return render(request, 'home.html', context)

    return render(request, 'home.html', context)
