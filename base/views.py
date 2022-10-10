from django.shortcuts import render

def index(request):
    return render(request, 'base/html/templates/index.html', {'message': "pumpkin pie"})