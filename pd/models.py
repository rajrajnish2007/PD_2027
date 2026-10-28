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

# Create your models here.
