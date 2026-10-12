from django import forms

#RAJNISH START
from .models import InstitutionalTeam


class InstitutionalTeamForm(forms.ModelForm):

    class Meta:
        model = InstitutionalTeam
        fields = ['institution_name', 'team_slots', 'adjudicator_slots', 'team_rep_names','contact_number', 'email', 'alt_contact_name',  'alt_contact_email', 'alt_contact_number']

        widgets = {
    'institution_name': forms.TextInput(attrs={
        'placeholder': 'Enter institution name',
    }),

    'team_slots': forms.NumberInput(attrs={
        'placeholder': 'Number of team slots required',
        'min': '0',
    }),

    'adjudicator_slots': forms.NumberInput(attrs={
        'placeholder': 'Number of adjudicator slots required',
        'min': '0',
    }),

    'team_rep_names': forms.TextInput(attrs={
        'placeholder': 'Enter team representative name',
    }),

    'contact_number': forms.TextInput(attrs={
        'placeholder': 'Enter 10-digit mobile number',
        'maxlength': '10',
        'inputmode': 'numeric',
    }),

    'email': forms.EmailInput(attrs={
        'placeholder': 'Preferably debate society email ID',
    }),

    'alt_contact_name': forms.TextInput(attrs={
        'placeholder': 'Enter alternate contact name (optional)',
    }),

    'alt_contact_email': forms.EmailInput(attrs={
        'placeholder': 'Enter alternate email address (optional)',
    }),

    'alt_contact_number': forms.TextInput(attrs={
        'placeholder': 'Enter alternate 10-digit mobile number',
        'maxlength': '10',
        'inputmode': 'numeric',
    }),
}
#RAJNISH END