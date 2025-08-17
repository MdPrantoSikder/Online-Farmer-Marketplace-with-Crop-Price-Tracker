from django import forms
from django.contrib.auth.models import User
from apps.accounts.models import Profile

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=255)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    role = forms.ChoiceField(choices=[("CUSTOMER", "Customer"), ("FARMER", "Farmer")])

    # Fields for Farmer
    image = forms.ImageField(required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        # Ensure passwords match
        if password != password2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data
