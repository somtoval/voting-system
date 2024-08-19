from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User # Default django user model
from .models import *
from django.forms import inlineformset_factory
from django.forms import modelformset_factory

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2'] # Normally if we just import UserCreationForm and render it in our page it will not output email field, so we are import the django built-in user model and customizing it based on the documentation, it has values like password1 and password2 and also email.

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name']

ElectionPositionFormset = inlineformset_factory(Election, Position, form=PositionForm, extra=1, can_delete=True)

class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['name', 'description', 'start_date', 'end_date']

class ContestantForm(forms.ModelForm):
    class Meta:
        model = Contestant
        fields = ['student', 'election', 'position']

# # Add this line at the end of your forms.py
# ContestantFormSet = modelformset_factory(Contestant, form=ContestantForm, extra=1, can_delete=True)