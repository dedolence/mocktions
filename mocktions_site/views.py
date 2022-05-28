import logging
from django.shortcuts import render

# set up logger
logger = logging.getLogger('heroku_stream')


def index(request):
    #logger.info("First time log set up!")
    return render(request, 'index.html', {})