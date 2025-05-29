from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import User


class SignUpUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')



# class SignUpUserForm(UserCreationForm):
#     email = forms.EmailField(max_length=254, help_text='Обязательное поле. Введите действующий email.')
#     password1 = forms.CharField(widget=forms.PasswordInput(), label="Пароль")
#     password2 = forms.CharField(widget=forms.PasswordInput(), label="Подтвердите пароль")
#
#     class Meta:
#         model = User
#         fields = ('username', 'email')  # Больше не указываем password1 и password2
#
#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         password2 = cleaned_data.get("password2")
#
#         if password != password2:
#             raise forms.ValidationError(
#                 "Пароли не совпадают"
#             )
#
#         return cleaned_data
#
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data["email"]
#         password = self.cleaned_data["password"] # Используем поле password, установленное UserCreationForm
#         user.set_password(password)  # Хешируем пароль
#         if commit:
#             user.save()
#         return user