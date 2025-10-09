from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from events.utils.error_logger import ErrorLogger
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import UserProfile

def register_view(request):
    if request.method == 'POST':
        ErrorLogger.log_purchase_flow('REGISTER_START', {
            'path': request.path,
            'method': request.method,
            'ip': request.META.get('REMOTE_ADDR'),
        })
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                # Criar perfil de usuário automaticamente
                UserProfile.objects.create(user=user)
                # Autenticar e fazer login do usuário
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password1')
                user = authenticate(request, username=email, password=password)
                login(request, user)
                ErrorLogger.log_object_state(user, 'REGISTER_SUCCESS')
                messages.success(request, 'Conta criada com sucesso!')
                return redirect('/')
        else:
            ErrorLogger.log_ticket_error(Exception('REGISTER_FORM_INVALID'), {
                'errors': form.errors.as_json(),
            })
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        ErrorLogger.log_purchase_flow('LOGIN_START', {
            'path': request.path,
            'method': request.method,
            'ip': request.META.get('REMOTE_ADDR'),
        })
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                ErrorLogger.log_object_state(user, 'LOGIN_SUCCESS')
                messages.success(request, f'Bem-vindo de volta, {user.name}!')
                return redirect('/')
            else:
                ErrorLogger.log_ticket_error(Exception('LOGIN_FAILED'), {
                    'email': email,
                })
                messages.error(request, 'Email ou senha inválidos.')
        else:
            ErrorLogger.log_ticket_error(Exception('LOGIN_FORM_INVALID'), {
                'errors': form.errors.as_json(),
            })
            messages.error(request, 'Email ou senha inválidos.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    ErrorLogger.log_purchase_flow('LOGOUT', {
        'user_id': getattr(request.user, 'id', None),
        'path': request.path,
    })
    logout(request)
    messages.success(request, 'Você saiu com sucesso.')
    return redirect('/')

@login_required
def profile_view(request):
    user = request.user
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'users/profile.html', {'form': form, 'user': user})

# Middleware para verificação de papéis
def role_required(roles):
    def decorator(view_func):
        @login_required
        def wrapped_view(request, *args, **kwargs):
            user_roles = [role.role for role in request.user.roles.all()]
            if any(role in user_roles for role in roles):
                return view_func(request, *args, **kwargs)
            messages.error(request, 'Você não tem permissão para acessar esta página.')
            return redirect('home')
        return wrapped_view
    return decorator
