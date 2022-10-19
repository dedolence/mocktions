from django.shortcuts import render
import logging

LOGGER = logging.getLogger('fly_stream')

def index(request):
    #logging.error("Testing error messages.")
    #LOGGER.info("Here's an info message using Django's Logging.")
    #LOGGER.error("Here's an error message using Django's Logging.")
    return render(request, 'base/html/templates/index.html', {'message': "pumpkin pie"})