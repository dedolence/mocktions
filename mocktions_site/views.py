from http.client import HTTPResponse
from django.shortcuts import render

# Create your views here.
def index(request):
    return HTTPResponse("Hello, world!")