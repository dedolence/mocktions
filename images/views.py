from django.views.generic import CreateView
from images.models import Image
from django.http import HttpRequest, HttpResponse
from typing import Any
from django.shortcuts import render
from images.test.test_form import TestForm
from django.template.loader import render_to_string

def test_view(request):
    """
        The goal is to return HTML that gets split into two space:
        1) the form is returned so that it includes any errors
        2) a new model instance, rendered to a template, is returned
        and placed at the beginning of a div without replacing the entire
        content of that div.
    """

    if request.method == "GET":
        form = TestForm()
        return render(request, "images/html/templates/test_index.html", {'form': form})
    
    if request.method == "POST":
        counter = int(request.POST["counter"])
        counter += 1
        form = TestForm()
        form_html = render_to_string("images/test/form.html", {'form': form, 'counter': counter}, request=request)
        list_item_html = render_to_string("images/test/list_item.html", {'counter': counter}, request=request)
        html = form_html + list_item_html
        return HttpResponse(html)