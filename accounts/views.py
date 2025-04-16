from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, 
    PasswordResetDoneView, PasswordResetConfirmView, 
    PasswordResetCompleteView
)
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserLoginForm, UserPasswordResetForm, UserSetPasswordForm, ProfileEditForm
from .models import UserProfile

# Create your views here.

class UserRegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        
        # Send verification email (you would implement this for production)
        if not settings.DEBUG:
            # Send verification email in production
            send_mail(
                'Verify your Travel Explorer account',
                f'Thank you for registering. Please verify your account by clicking this link: {self.request.build_absolute_uri("/verify/" + str(user.id))}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        
        messages.success(self.request, 'Registration successful! Please log in.')
        return super().form_valid(form)

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    
    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me', False)
        if not remember_me:
            # Session expires when user closes browser
            self.request.session.set_expiry(0)
        
        # Check if user is verified
        user = form.get_user()
        if not user.profile.is_verified:
            messages.error(self.request, 'Please verify your email before logging in.')
            return self.form_invalid(form)
            
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('home')

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    form_class = UserPasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'

class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = UserSetPasswordForm
    success_url = reverse_lazy('password_reset_complete')

class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

@login_required
def profile_view(request):
    """View for user profile"""
    context = {}
    
    # Process travel history
    if request.user.profile.travel_history:
        try:
            import json
            # Parse travel history from JSON
            travel_history = json.loads(request.user.profile.travel_history)
            context['travel_history'] = travel_history
        except json.JSONDecodeError:
            # Handle legacy comma-separated format
            travel_places = [place.strip() for place in request.user.profile.travel_history.split(',')]
            context['travel_places'] = travel_places
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """View for editing user profile"""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user.profile, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user.profile, user=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

def verify_email(request, user_id):
    """View to verify user email"""
    try:
        user = User.objects.get(id=user_id)
        user.profile.is_verified = True
        user.profile.save()
        messages.success(request, 'Email verified! You can now log in.')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification link')
    
    return redirect('login')
