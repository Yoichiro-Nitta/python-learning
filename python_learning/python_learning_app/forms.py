from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class SignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    pass


class ContactForm(forms.Form):
    """お問い合わせフォーム"""
    # フィールド
    name = forms.CharField(max_length=40, error_messages={'required': '必須項目です'})
    email = forms.EmailField(error_messages={'required': '必須項目です'})
    title = forms.CharField(max_length=60, required=False)
    message = forms.CharField(error_messages={'required': '必須項目です'})