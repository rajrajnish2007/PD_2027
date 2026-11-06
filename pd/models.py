from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

phone_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message="Enter a valid 10-digit Indian mobile number."
)


class IndependentAdjudicator(models.Model):
    name = models.CharField(max_length=255)
    institution_name = models.CharField(max_length=255)

    contact_number = models.CharField(
        max_length=10,
        validators=[phone_validator]
    )

    email = models.EmailField()

    alternate_contact_number = models.CharField(
        max_length=10,
        validators=[phone_validator],
        blank=True,
        null=True
    )

    alternate_email = models.EmailField(
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if (
            self.contact_number
            and self.alternate_contact_number
            and self.contact_number == self.alternate_contact_number
        ):
            raise ValidationError(
                "Primary and alternate contact numbers must be different."
            )

        if (
            self.email
            and self.alternate_email
            and self.email == self.alternate_email
        ):
            raise ValidationError(
                "Primary and alternate emails must be different."
            )

    def __str__(self):
        return self.name

# RAJNISH START
class InstitutionalTeam(models.Model):
    # mandatory
    phone_validator = RegexValidator(
        regex=r'^(\+?91[\s-]?)?[6-9][0-9]{4}[\s-]?[0-9]{5}$',
        message="Enter a valid 10-digit indian phone number(starting with digit 6-9).",
    )
    institution_name = models.CharField("name of institution", unique=True, max_length=200)
    team_slots = models.PositiveSmallIntegerField("number of team slots required")
    adjudicator_slots = models.PositiveSmallIntegerField("number of adjudicator slots required")
    team_rep_names = models.CharField("team representative name(s)", max_length=300)
    contact_number = models.CharField("contact number", max_length=15, validators=[phone_validator])
    email = models.EmailField("email ID", error_messages={"invalid": "Please enter a valid email address, like ranjo@example.com."})
   

    # optional
    alt_contact_name = models.CharField("alternate contact name", max_length=100, blank=True)
    alt_contact_email = models.EmailField("alternate contact email", blank=True, error_messages={"invalid": "Please enter a valid email address, like ranjo@example.com."})
    alt_contact_number = models.CharField("alternate contact number", max_length=15, blank=True, validators=[phone_validator])

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.institution_name

    def clean(self):
        errors = {}

        if self.team_slots == 0 and self.adjudicator_slots == 0:
            errors["team_slots"] = "At least one team or adjudicator slot must be requested."
            errors["adjudicator_slots"] = "At least one team or adjudicator slot must be requested."

        if self.alt_contact_name and self.team_rep_names and self.alt_contact_name.strip().casefold() == self.team_rep_names.strip().casefold():
            errors["alt_contact_name"] = "Alternate point of contact name must be different from team representative name."

        if self.alt_contact_email and self.email and self.alt_contact_email.strip().lower() == self.email.strip().lower():
            errors["alt_contact_email"] = "Alternate email must be different from the main email."

        if self.alt_contact_number and self.contact_number:
            norm_alt = self.alt_contact_number.replace("+91", "").replace(" ", "").replace("-", "")
            norm_main = self.contact_number.replace("+91", "").replace(" ", "").replace("-", "")
            if norm_alt == norm_main:
                errors["alt_contact_number"] = "Alternate number must be different from the main contact number."

        if errors:
            raise ValidationError(errors)
    #RAJNISH END


# RAJNISH START
class CrossTeam(models.Model):
    phone_validator = RegexValidator(
        regex=r'^(\+?91[\s-]?)?[6-9][0-9]{4}[\s-]?[0-9]{5}$',
        message="Enter a valid 10-digit indian phone number(starting with digit 6-9).",
    )

    # mandatory fields
    team_name = models.CharField("name of team", max_length=200, unique=True)
    adjudicator_slots = models.PositiveSmallIntegerField("number of adjudicator slots required", default=0)
    team_leader_name = models.CharField("name of team leader", max_length=200)
    contact_number = models.CharField("contact number", max_length=15, validators=[phone_validator])
    email = models.EmailField("email ID", error_messages={"invalid": "Please enter a valid email address."})

    # optional alternate fields
    alt_contact_name = models.CharField("alternate contact name", max_length=100, blank=True)
    alt_contact_number = models.CharField("alternate contact number", max_length=15, blank=True, validators=[phone_validator])
    alt_contact_email = models.EmailField("alternate contact email", blank=True, error_messages={"invalid": "Please enter a valid email address."})

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cross/Open Team"
        verbose_name_plural = "Cross/Open Teams"

    def __str__(self):
        return self.team_name

    def clean(self):
        errors = {}

        if self.alt_contact_name and self.team_leader_name and self.alt_contact_name.strip().casefold() == self.team_leader_name.strip().casefold():
            errors["alt_contact_name"] = "Alternate point of contact name must be different from team leader name."

        if self.alt_contact_email and self.email and self.alt_contact_email.strip().lower() == self.email.strip().lower():
            errors["alt_contact_email"] = "Alternate email must be different from the main email."

        if self.alt_contact_number and self.contact_number:
            norm_alt = self.alt_contact_number.replace("+91", "").replace(" ", "").replace("-", "")
            norm_main = self.contact_number.replace("+91", "").replace(" ", "").replace("-", "")
            if norm_alt == norm_main:
                errors["alt_contact_number"] = "Alternate number must be different from the main contact number."

        if errors:
            raise ValidationError(errors)
# RAJNISH END
