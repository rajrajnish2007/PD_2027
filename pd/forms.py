from django import forms
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