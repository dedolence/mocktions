from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.forms import RegistrationForm


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('accounts:profile'))
    else:
        return HttpResponseRedirect(reverse('accounts:login'))


def profile(request):
    pass


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
