from django.contrib import messages
from django.contrib.auth.views import logout_then_login
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView

from accounts.forms import RegistrationForm

from .strings import en as english_strings


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        return HttpResponseRedirect(reverse('accounts:login'))


class Logout(View):
    success_message = "You have been logged out."
    def post(self, request):
        messages.success(request, self.success_message)
        return logout_then_login(request, login_url=reverse('accounts:login'))


class Profile(View):
    """
        Why just redirect? Because the reverse to index here isn't available in
        accounts.urls, so it can't be set in the URL path for login's redirect URL.
    """
    def get(self, request):
        return HttpResponseRedirect(reverse('base:index'))

    def post(self, request):
        # to be used for setting user's profile information
        pass


class Register(SuccessMessageMixin, CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/html/templates/register.html'

    def get_success_message(self, cleaned_data) -> str:
        """
            Format the success message to include the user's username.
        """
        return english_strings.REGISTRATION_SUCCESS.format(
            username=self.object.username
        )
