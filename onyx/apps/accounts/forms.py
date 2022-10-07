from django import forms
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Introducir contraseña',
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirmar contraseña'
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "¡Las contraseñas no coinciden!"
            )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Ingrese el nombre'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Ingrese el apellido'
       
        self.fields['email'].widget.attrs['placeholder'] = 'Ingrese el email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Solo archivos de imagen")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('city', 'country', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'




