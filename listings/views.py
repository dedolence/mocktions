from django.shortcuts import render
import django.views.generic as views 
from listings.models import Listing
from django.db.models import QuerySet
from typing import Any, Dict
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from listings.forms import ListingForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from images.models import ImageSet

class ListingBase():
    model = Listing
    context_object_name = "listing"


class ListingOwnerOnly():
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            return HttpResponseRedirect(reverse_lazy("base:index"))
        
        return super().dispatch(request, *args, **kwargs)


class HX_List(ListingBase, views.ListView):
    """
        To insert a list of listings, add
        {% include 'listings/html/includes/main.html with list_by=user|all %}
        to any template. The template will make an AJAX HTMX call to this view
        which returns HTML that gets swapped into the DOM.
    """
    allow_empty = True
    context_object_name = "listings"    # the context variable name in templates
    list_by_values = ["all", "user"]    # specify queryset
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
    

class ListingCreate(LoginRequiredMixin, ListingBase, views.CreateView):
    """ 
        Creates a new model instance and returns HTML to be swapped into
        the DOM by HTMX.
    """
    form_class = ListingForm
    template_name = "listings/html/templates/create.html"
    extra_context = {}

    def form_valid(self, form: ListingForm) -> HttpResponse:
        form.instance.user = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(reverse_lazy("listings:detail", args=[self.object.id]))
    
    def form_invalid(self, form: ListingForm) -> HttpResponse:
        """ 
            In order to not lose any previously uploaded images, make sure the new imageset
            is included in the template's context data.
        """
        self.extra_context["imageset"] = ImageSet.objects.get(pk=form["imageset"].value())
        return super().form_invalid(form)
    

class ListingDetail(ListingBase, views.DetailView):
    template_name = "listings/html/templates/detail.html"


class ListingUpdate(
        SuccessMessageMixin,
        LoginRequiredMixin, 
        ListingBase, 
        ListingOwnerOnly, 
        views.UpdateView): 
    form_class = ListingForm
    template_name = "listings/html/templates/create.html"
    success_message = "Listing updated."


class ListingDelete(
        SuccessMessageMixin, 
        LoginRequiredMixin, 
        ListingBase, 
        ListingOwnerOnly, 
        views.DeleteView):
    """
        To do: check there are no bids on the listing before deleting.
    """
    success_url = reverse_lazy("base:index")
    template_name = "listings/html/templates/delete.html"
    
    def get_success_message(self, cleaned_data: Dict[str, str]) -> str:
        title = self.object.title 
        return f"Listing, \"{title}\" has been deleted."