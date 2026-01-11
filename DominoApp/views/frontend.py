import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render

def home(request):
    return render(request, "DominoApp/home.html")


def custom_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == "test" and password == "test":
            request.session["user"] = username
            return redirect("home")
        else:
            messages.error(request, "Nieprawidłowe dane logowania")

    return render(request, "DominoApp/login.html")


def dashboard_view(request):
    return render(request, "DominoApp/dashboard.html")

def buildings_list_view(request):
    return render(request, "DominoApp/buildings.html")

def building_details_view(request, building_id):
    return render(request, "DominoApp/building_details.html", {'building_id': building_id})

def flat_details_view(request, building_id, flat_id):
    return render(request, "DominoApp/flat_details.html", {
        'building_id': building_id,
        'flat_id': flat_id
    })

def profile_view(request):
    return render(request, "DominoApp/profile.html")

def announcements_view(request):
    return render(request, "DominoApp/announcements.html")

def my_flats_view(request):
    return render(request, "DominoApp/my_flats.html")

def my_rents_view(request):
    return render(request, "DominoApp/my_rents.html")

def my_reports_view(request):
    return render(request, "DominoApp/my_reports.html")

def admin_reports_view(request):
    return render(request, "DominoApp/admin_reports.html")

def admin_users_view(request):
    return render(request, "DominoApp/admin_users.html")




