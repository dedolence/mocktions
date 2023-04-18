from django.shortcuts import render
import django.views.generic as views 
from listings.models import Listing
from django.db.models import QuerySet
from typing import Any, Dict
from django.http import HttpRequest, HttpResponse


class HX_List(views.ListView):
    """
        To insert a list of listings, add
        {% include 'listings/html/includes/main.html with list_by=user|all %}
        to any template. The template will make an AJAX HTMX call to this view
        which returns HTML that gets swapped into the DOM.
    """
    allow_empty = True
    context_object_name = "listings"    # the context variable name in templates
    list_by_values = ["all", "user"]    # specify queryset
    model = Listing
    template_name = "listings/html/includes/list.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        list_by = request.GET.get("list_by", "user")

        if list_by not in self.list_by_values:
            list_by = "user"

        match list_by:
            case "all":
                self.queryset = Listing.objects.all()
            case "user":
                self.queryset = request.user.listings.all()
            case other:
                self.queryset = Listing.objects.all()

        return super().get(request, *args, **kwargs)
    

class HX_Create(views.CreateView):
    """ 
        Creates a new model instance and returns HTML to be swapped into
        the DOM by HTMX.
    """
    model = Listing