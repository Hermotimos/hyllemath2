from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# from users.models import Profile


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = "EMAIL"
        self.fields['username'].label = "LOGIN"


class UserImageUpdateForm(forms.Form):
    user_image = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_image'].label = "ZMIEŃ AWATAR UŻYTKOWNIKA (wymiary kwadratu!)"


# class ProfileUpdateForm(forms.ModelForm):

#     class Meta:
#         model = Profile
#         fields = ['image']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['image'].label = "AWATAR POSTACI (wymiary kwadratu!)"
