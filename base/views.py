from django.shortcuts import render
import logging
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseServerError
from django.views.generic import TemplateView

LOGGER = logging.getLogger('fly_stream')

def index(request):
    #logging.error("Testing error messages.")
    #LOGGER.info("Here's an info message using Django's Logging.")
    #LOGGER.error("Here's an error message using Django's Logging.")
    return render(request, 'base/html/templates/index.html', {'message': "pumpkin pie"})

""" 
def handler403(request, exception):
    return HttpResponseForbidden(
        render(request, 'base/html/templates/403.html')
    )
 """

def handler403(request, exception):
    print(request.path)
    return HttpResponseForbidden(
        render(request, 'base/html/templates/error.html')
    )


def handler404(request, exception):
    return HttpResponseBadRequest(
        render(request, 'base/html/templates/404.html')
        )


def handler500(request):
    return HttpResponseServerError(
        render(request, 'base/html/templates/500.html')
        )
