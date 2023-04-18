from django.shortcuts import render
import django.views.generic as views 
from listings.models import Listing
from django.db.models import QuerySet
from typing import Any, Dict
from django.http import HttpRequest, HttpResponse

class List(views.ListView):
    context_object_name = "listings"
    allow_empty = True
    model = Listing
    list_by_values = ["all", "user"]
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

        return super().get(request, *args, **kwargs)