from django.shortcuts import render,redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.
#RAJNISH START
from .forms import InstitutionalTeamForm

def home(request):
    return render(request, "home.html")

def register_institutional(request):
    if request.method == "POST":
        form = InstitutionalTeamForm(request.POST)
        if form.is_valid():
            instance = form.save()

            messages.success(request, "Registration submitted successfully!")
            
            send_mail(
                subject="Institutional Team Registration Confirmation - Alcheringa",
                message=(
                    f"Hi {instance.institution_name} Team,\n\n"
                    "Your institutional team registration has been received successfully.\n"
                    "We'll contact you soon with further details.\n\n"
                    "Regards,\nAlcheringa"
                ),
                from_email=(
                    getattr(settings, "EMAIL_HOST_USER", None)
                    or getattr(settings, "DEFAULT_FROM_EMAIL", None)
                ),
                recipient_list=[instance.email],
                fail_silently=True,
            )

            return redirect('registration:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = InstitutionalTeamForm()

    return render(request, "register_institutional.html", {"form": form})
    #RAJNISH END


#Ashmitha START
from .forms import IndependentAdjudicatorForm


def register_adjudicator(request):
    if request.method == "POST":
        form = IndependentAdjudicatorForm(request.POST)

        if form.is_valid():
            instance = form.save()

            messages.success(
                request,
                "Registration submitted successfully!"
            )

            send_mail(
                subject="Adjudicator Registration Confirmation - Alcheringa",
                message=(
                    f"Hi {instance.name},\n\n"
                    "Your adjudicator registration has been received successfully.\n"
                    "We’ll contact you soon with the next steps.\n\n"
                    "Regards,\nAlcheringa"
                ),
                from_email=(
                    getattr(settings, "EMAIL_HOST_USER", None)
                    or getattr(settings, "DEFAULT_FROM_EMAIL", None)
                ),
                recipient_list=[instance.email],
                fail_silently=True,
            )

            return redirect("registration:register_adjudicator")

    else:
        form = IndependentAdjudicatorForm()

    return render(
        request,
        "pd/register_adjudicator.html",
        {"form": form}
    )
#Ashmitha END


# RAJNISH START
from .forms import CrossTeamForm


def register_cross(request):
    if request.method == "POST":
        form = CrossTeamForm(request.POST)
        if form.is_valid():
            instance = form.save()

            messages.success(request, "Registration submitted successfully!")

            send_mail(
                subject="Cross/Open Team Registration Confirmation - Alcheringa",
                message=(
                    f"Hi {instance.team_name} Team,\n\n"
                    "Your cross/open team registration has been received successfully.\n"
                    "We'll contact you soon with further details.\n\n"
                    "Regards,\nAlcheringa"
                ),
                from_email=(
                    getattr(settings, "EMAIL_HOST_USER", None)
                    or getattr(settings, "DEFAULT_FROM_EMAIL", None)
                ),
                recipient_list=[instance.email],
                fail_silently=True,
            )

            return redirect('registration:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CrossTeamForm()

    return render(request, "register_cross.html", {"form": form})
# RAJNISH END
