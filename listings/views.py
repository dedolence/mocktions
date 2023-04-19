from django.shortcuts import render
import django.views.generic as views 
from listings.models import Listing
from django.db.models import QuerySet
from typing import Any, Dict
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from listings.forms import ListingForm
from django.contrib.messages.views import SuccessMessageMixin

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
        list_by = request.GET.get("list_by", None)

        match list_by:
            case "all":
                self.queryset = Listing.objects.all()
            case "user":
                self.queryset = request.user.listings.all()
            case None:
                self.queryset = Listing.objects.all()

        return super().get(request, *args, **kwargs)
    

class ListingCreate(views.CreateView):
    """ 
        Creates a new model instance and returns HTML to be swapped into
        the DOM by HTMX.
    """
    model = Listing
    form_class = ListingForm
    template_name = "listings/html/templates/create.html"

    def form_valid(self, form: ListingForm) -> HttpResponse:
        form.instance.user = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(reverse_lazy("listings:detail", args=[self.object.id]))
    

class ListingDetail(views.DetailView):
    model = Listing
    context_object_name = "listing"
    template_name = "listings/html/templates/detail.html"


class ListingUpdate(views.UpdateView):
    model = Listing 
    context_object_name = "listing"
    form_class = ListingForm
    template_name = "listings/html/templates/create.html"


class ListingDelete(SuccessMessageMixin, views.DeleteView):
    """
        To do: check there are no bids on the listing before deleting.
    """
    model = Listing
    context_object_name = "listing"
    success_url = reverse_lazy("base:index")
    template_name = "listings/html/templates/delete.html"
    
    def get_success_message(self, cleaned_data: Dict[str, str]) -> str:
        title = self.object.title 
        return f"Listing, \"{title}\" has been deleted."