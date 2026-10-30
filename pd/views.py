from django.shortcuts import render,redirect
# Create your views here.
#RAJNISH START
from django.contrib import messages
from .models import InstitutionalTeam
from .forms import InstitutionalTeamForm

def home(request):
    return render(request, "home.html")

def register_institutional(request):
    if request.method == "POST":
        form = InstitutionalTeamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration submitted successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = InstitutionalTeamForm()

    return render(request, "register_institutional.html", {"form": form})
    #RAJNISH END