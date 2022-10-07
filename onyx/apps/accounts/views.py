from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
#from django.http import HttpResponse
# Create your views here.

# Verification email

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            #phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            #user.phone_number = phone_number
            user.save()

            # Create a user profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-1.jpeg'
            profile.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Activa tu cuenta'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            #messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address [rathan.kumar@gmail.com]. Please verify it.')
            return redirect('/accounts/login/?command=verification&email='+email)
                      
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:      

            auth.login(request, user)
            messages.success(request, 'Ahora está conectado.')
            
            return redirect('dashboard')
            
        else:
            messages.error(request, 'Credenciales de acceso invalidos')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Estás desconectado.')
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Felicidades su cuenta ha sido activada')
        return redirect('login')
    else:
        messages.error(request, 'Enlace de activación no válido')
        return redirect('register')


@login_required(login_url = 'login')
def dashboard(request):
    
    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        #'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Restablecer su contraseña'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Se ha enviado un correo electrónico para restablecer la contraseña a su dirección de correo electrónico.')
            return redirect('login')
        else:
            messages.error(request, '¡La cuenta no existe!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'por favor, cambie su contraseña')
        return redirect('resetPassword')
    else:
        messages.error(request, '¡Este enlace ha caducado!')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Restablecimiento de contraseña exitosa')
            return redirect('login')
        else:
            messages.error(request, '¡La contraseña no coincide!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Tu perfil ha sido actualizado.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Contraseña actualizada exitosamente.')
                return redirect('change_password')
            else:
                messages.error(request, 'Ingrese una contraseña actual válida')
                return redirect('change_password')
        else:
            messages.error(request, '¡Las contraseñas no coinciden!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')


