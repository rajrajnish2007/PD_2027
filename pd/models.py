from django.db import models

# RAJNISH START
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
        regex=r'^[6-9][0-9]{9}$',
        message="Enter a valid 10-digit indian phone number(starting with digit 6-9).",
)



class InstitutionalTeam(models.Model):
    # mandatory
    institution_name = models.CharField("name of institution", max_length=200)
    team_slots = models.PositiveSmallIntegerField("number of team slots required")
    adjudicator_slots = models.PositiveSmallIntegerField("number of adjudicator slots required")
    team_rep_names = models.CharField("team representative name(s)", max_length=300)
    contact_number = models.CharField("contact number", max_length=10, validators=[phone_validator])
    email = models.EmailField("email ID", error_messages={"invalid": "Please enter a valid email address, like ranjo@example.com."})
   

    # optional
    alt_contact_name = models.CharField("alternate contact name", max_length=100, blank=True)
    alt_contact_email = models.EmailField("alternate contact email", blank=True, error_messages={"invalid": "Please enter a valid email address, like ranjo@example.com."})
    alt_contact_number = models.CharField("alternate contact number", max_length=10, blank=True, validators=[phone_validator])

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.institution_name

    def clean(self):
        errors = {}

        if self.team_slots == 0 and self.adjudicator_slots == 0:
            errors["team_slots"] = "At least one team or adjudicator slot must be requested."
            errors["adjudicator_slots"] = "At least one team or adjudicator slot must be requested."

        
        if self.alt_contact_email and self.alt_contact_email.lower() == self.email.lower():
            errors["alt_contact_email"] = "Alternate email must be different from the main email."

        if self.alt_contact_number and self.alt_contact_number == self.contact_number:
            errors["alt_contact_number"] = "Alternate number must be different from the main contact number."

        if errors:
            raise ValidationError(errors)   
    #RAJNISH END