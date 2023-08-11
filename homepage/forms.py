from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models.fields import EmailField
from django.forms import fields
from django.forms.widgets import PasswordInput, Widget
from django.http import request
from phonenumbers import phonenumber
from homepage.models import Product, Customer
from django import forms
from django.forms import ModelForm
from phonenumber_field.formfields import PhoneNumberField
from django_countries import Countries

class HomeForm(forms.Form):
    productURL = forms.CharField(label="", max_length="1000")


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email already used")
        return email

    def clean_username(self):
        data = self.cleaned_data['username']
        if not data.islower():
            raise forms.ValidationError("Usernames should be in lowercase")
        if '@' in data or '-' in data or '|' in data:
            raise forms.ValidationError(
                "Usernames should not have special characters.")
        return data


class UserLoginForm(forms.Form):
    usernameSignIn = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control",}))
    passwordSignIn = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "form-control"}))
supportedCountries= (
        ('US',"United States of America"),
        ('GB',"United Kingdom"),
    )

class CustomerForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control", "autocomplete": "new-password"}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={"class": "form-control", "autocomplete": "new-password"}))
    country = forms.ChoiceField(widget=forms.Select(
        attrs={"class": "form-control"}), choices=supportedCountries, required=False)
    phonenumber = PhoneNumberField(widget=forms.TextInput(attrs={"id":"phoneNumber","class": "form-control"}),required=False)


    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():

            if email == User.objects.get(email=email).email:
                pass
            else:
                raise forms.ValidationError("This email already used")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if '@' in username or '-' in username or '|' in username:
            raise forms.ValidationError(
                "Usernames should not have special characters.")

        if User.objects.filter(username=username).exists():

            if username == User.objects.get(username=username).username:
                pass
            else:
                raise forms.ValidationError("username in use")
        return username


class changeEmail1(forms.Form):
    changeEmail = forms.EmailField(widget=forms.EmailInput(
        attrs={"class": "form-control", "autocomplete": "new-password"}))

    def clean_email(self):
        userEmail = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():

            if userEmail == User.objects.get(email=userEmail).email:
                pass
            else:
                raise forms.ValidationError("This email already used")
        return userEmail
class changePassword(forms.Form):
    oldPassword = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "form-control mb-2 mt-2", "placeholder": "Enter your old password"}))
    passwordnew = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "form-control mb-2", "placeholder": "New password"}))
    passwordnew1 = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "form-control mb-2", "placeholder": "Confirm new password"}))
