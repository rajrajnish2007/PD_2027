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
        'maxlength': '15',
        'inputmode': 'tel',
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
        'maxlength': '15',
        'inputmode': 'tel',
    }),
}
#RAJNISH END

#Ashmitha START
from .models import IndependentAdjudicator


class IndependentAdjudicatorForm(forms.ModelForm):
    class Meta:
        model = IndependentAdjudicator
        fields = [
            'name',
            'institution_name',
            'contact_number',
            'email',
            'alternate_contact_number',
            'alternate_email',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name*'}),
            'institution_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'College/Institution Name*'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number*'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email ID*'}),
            'alternate_contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alternate Contact Number'}),
            'alternate_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Alternate Email ID'}),
        }
#Ashmitha End