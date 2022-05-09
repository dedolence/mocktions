import logging
from django.http import HttpResponse
from django.shortcuts import render

# set up logger
logger = logging.getLogger(__name__)


def index(request):
    logger.info("First time log set up!")
    return render(request, 'mocktions_site/index.html', {})