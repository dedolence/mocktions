from curses.ascii import HT
from django.contrib import messages
from django.contrib.auth.views import logout_then_login, LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, DeleteView

from accounts.forms import RegistrationForm

from .strings import en as strings
from .models import User
from .forms import DeleteAccountForm, LoginForm


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        return HttpResponseRedirect(reverse('accounts:login'))


class DeleteAccount(SuccessMessageMixin, DeleteView):
    form_class = DeleteAccountForm
    model = User
    success_url = reverse_lazy('base:index')
    template_name = 'accounts/html/templates/delete_account.html'
    success_message = strings.ACCOUNT_DELETE_SUCCESS


class Login(SuccessMessageMixin, LoginView):
    template_name = 'accounts/html/templates/login.html'
    form_class = LoginForm
    def get_success_url(self) -> str:
        return reverse_lazy(
            'accounts:profile', 
            kwargs={
                'pk': self.request.user.id
            }
        )

class Logout(View):
    success_message = strings.LOGOUT_MESSAGE

    def get(self, request):
        return render(request, 'accounts/html/templates/logout.html')

    def post(self, request):
        messages.success(request, self.success_message)
        return logout_then_login(request, login_url=reverse('accounts:login'))


class Profile(DetailView):
    """
        In templates, Django automatically passes the model instance as a
        variable that is the lowercase version of the model name, in this
        case: user. Therefore, in the template, the instance can be accessed
        such as {{ user.username }}.
    """
    model = User
    template_name = 'accounts/html/templates/profile.html'


class Register(SuccessMessageMixin, CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/html/templates/register.html'

    def get_success_message(self, cleaned_data) -> str:
        """
            Format the success message to include the user's username.
        """
        return strings.REGISTRATION_SUCCESS.format(
            username=self.object.username
        )
