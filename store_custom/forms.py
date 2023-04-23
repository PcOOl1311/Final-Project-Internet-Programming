from django import forms
from store.models import Customer


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone', 'birth_date', 'membership']
