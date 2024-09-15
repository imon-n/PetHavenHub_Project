from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.views import View
from django.contrib import messages
from .forms import UserRegistrationForm,UserUpdateForm
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.contrib.auth.forms import PasswordChangeForm
from pets.models import Pet_Model

from django.views.generic.edit import FormView
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str  
from django.contrib.auth.tokens import default_token_generator
from .models import User
from django.contrib.auth.models import User

class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('homepage')
    
    def form_valid(self, form):
        user = form.save()
        self.send_confirmation_email(user)
        return super().form_valid(form)

    def send_confirmation_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        messages.success(self.request, 'Check your E-mail inbox for Confirmations')
        confirm_link = self.request.build_absolute_uri(f'/accounts/activate/{uid}/{token}/')
        email_subject = "Confirm Your Email"
        email_body = render_to_string('accounts/confirm_email.html', {'confirm_link': confirm_link})
        email = EmailMessage(subject=email_subject, body=email_body, to=[user.email])
        email.content_subtype = "html" 
        email.send()


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('homepage')  
    else:
        return render(request, 'accounts/activation_invalid.html')



def send_transaction_email(user, subject, template):
    message = render_to_string(template, {'user' : user,})
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()


@login_required
def author_post_pets(request):
    posts = Pet_Model.objects.filter(author=request.user)
    return render(request, 'accounts/author_post_pets.html', {'posts': posts})


# class UserRegistrationView(FormView):
#     template_name = 'accounts/user_registration.html'
#     form_class = UserRegistrationForm
#     success_url = reverse_lazy('homepage')
#     def form_valid(self,form):
#         user = form.save()
#         login(self.request, user)
#         # send_transaction_email(user, 'Welcome to Our Site', 'accounts/welcome_email.html')
#         return super().form_valid(form)

class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('homepage')


@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


class UserAccountUpdateView(View):
    template_name = 'accounts/profile.html'
    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})
    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class PasswordChangeView(PasswordChangeView):
    template_name = 'accounts/pass_change.html'
    success_url = reverse_lazy('home')
    def form_valid(self, form):
        messages.success(self.request, 'Password Changed Successfully')
        update_session_auth_hash(self.request, form.user)
        # send_transaction_email(form.user, 'Password Changed Successfully', 'accounts/pass_change_email.html')
        return super().form_valid(form)