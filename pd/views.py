
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

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
