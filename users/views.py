from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth import authenticate, login, logout
from django.db.models import Value, Count, CharField
from django.contrib.auth.models import User
from pdf.models import User_profile
from pdf.views import get_user_history
from .facadeGoogleDrive import *

from pdf import auth
from apiclient.discovery import build
from httplib2 import Http

# Create your views here.

def about(request):
    return render(request, "users/about.html")

def index(request) :
    if not request.user.is_authenticate :
        return HttpResponseRedirect('index.html')
    return render(request , 'about.html')

def login_view(request) :
    # Check if user is already logged in
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST' :
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request , username = username , password = password)
        if user is not None :
            login(request , user)
            return HttpResponseRedirect(reverse('index'))
        else :
            return render(request , "users/index.html", {
                "message" : "Invalid Credential"
                })
    return render(request , 'users/index.html')

def logout_view(request) :
    logout(request)
    return render(request , 'pdf/upload.html' , {
        "message" : "Logged out"
    })

def register(request) :
    if request.method == 'POST' and (request.POST['password'] == request.POST['repeated_password']):
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        if not User.objects.filter(username = username).exists() :
            user = User.objects.create_user(username = username , password = password , email = email)
            GoogleDrive().create_folder(user)
            return HttpResponseRedirect(reverse('login'))
        else :
            return render(request , 'users/register.html' , {
                "message" : "username has been used"
            })
    elif request.method == 'POST' and (request.POST['password'] != request.POST['repeated_password']):
        return render(request , 'users/register.html' , {
            "message" : "Password did not match"
        })
    return render(request , 'users/register.html')

def history(request) :
    folder_id = User_profile.objects.get(ezpdf_user = request.user).folder_id
    history = get_user_history(folder_id)
    return render(request , "users/history.html" , {
        "history" : history
    })