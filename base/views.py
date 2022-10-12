from django.shortcuts import render
import logging

LOGGER = logging.getLogger('heroku_stream')

def index(request):
    LOGGER.info("------------\nLogging initiated.\n------------")
    return render(request, 'base/html/templates/index.html', {'message': "pumpkin pie"})