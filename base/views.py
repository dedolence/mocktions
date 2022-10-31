from django.shortcuts import render
import logging
from django.http import HttpResponseBadRequest, HttpResponseServerError

LOGGER = logging.getLogger('fly_stream')

def index(request):
    #logging.error("Testing error messages.")
    #LOGGER.info("Here's an info message using Django's Logging.")
    #LOGGER.error("Here's an error message using Django's Logging.")
    return render(request, 'base/html/templates/index.html', {'message': "pumpkin pie"})


def handler404(request, exception):
    return HttpResponseBadRequest(
        render(request, 'base/html/templates/404.html')
        )


def handler500(request):
    return HttpResponseServerError(
        render(request, 'base/html/templates/500.html')
        )
