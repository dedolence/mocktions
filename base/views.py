from django.shortcuts import render
import logging
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseServerError
from django.views.generic import TemplateView
from .strings import en

LOGGER = logging.getLogger('fly_stream')

def index(request):
    #logging.error("Testing error messages.")
    #LOGGER.info("Here's an info message using Django's Logging.")
    #LOGGER.error("Here's an error message using Django's Logging.")
    return render(request, 'base/html/templates/index.html', {'message': "pumpkin pie"})


def handler403(request, exception):
    context = {
        'error_header': en.PERMISSION_DENIED_H,
        'error_message': en.PERMISSION_DENIED_P
    }
    exception_class = HttpResponseForbidden
    return error_handler(request, exception_class, context, exception)


def handler404(request, exception):
    context = {
        'error_header': en.PAGE_NOT_FOUND_H,
        'error_message': en.PAGE_NOT_FOUND_P
    }
    exception_class = HttpResponseBadRequest
    return error_handler(request, exception_class, context, exception)


def handler500(request):
    context = {
        'error_header': en.SERVER_ERROR_H,
        'error_message': en.SERVER_ERROR_P
    }
    exception_class = HttpResponseServerError
    return error_handler(request, exception_class, context)


def error_handler(request, exception_class, context, exception=None):
    return exception_class(
        render(request, 'base/html/templates/error.html', context)
    )