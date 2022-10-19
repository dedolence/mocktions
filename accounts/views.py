from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import logout_then_login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from accounts.forms import RegistrationForm


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

class Register(View):
    form_class = RegistrationForm()
    registration_template = 'accounts/html/templates/register.html'
    def get(self, request):
        return render(request, self.registration_template, {
            'form': self.form_class
        })

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            # create and authenticate user
            user = form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
                )
            login(request, user)
            
            # set profile picture, if provided
            """ image_ids = request.POST.getlist('images', None)
            if (image_ids):
                image_id = image_ids[0]
                image = UserImage.objects.get(pk=image_id)
                image.owner = user
                image.save()
                user.profile_pic = image
                user.save() """
            
            """ # create a welcome message
            notification.build(
                user,
                TYPE_SUCCESS,
                ICON_SUCCESS,
                MESSAGE_REG_SUCCESS,
                False,
                reverse('index')
            )
            notification.save() """

            return HttpResponseRedirect(reverse('base:index'))
        else:
            return render(request, self.registration_template, {
                'form': form
            })


def register(request):
    if request.method == 'GET':
        form = RegistrationForm()
        return render(request, 'accounts/html/templates/register.html', {
            'form': form
        })
    else:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # create and authenticate user
            user = form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
                )
            login(request, user)
            
            # set profile picture, if provided
            """ image_ids = request.POST.getlist('images', None)
            if (image_ids):
                image_id = image_ids[0]
                image = UserImage.objects.get(pk=image_id)
                image.owner = user
                image.save()
                user.profile_pic = image
                user.save() """
            
            """ # create a welcome message
            notification.build(
                user,
                TYPE_SUCCESS,
                ICON_SUCCESS,
                MESSAGE_REG_SUCCESS,
                False,
                reverse('index')
            )
            notification.save() """

            return HttpResponseRedirect(reverse('base:index'))
        else:
            return render(request, 'accounts/html/templates/register.html', {
                'form': form
            })
