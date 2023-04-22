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
from globals import LISTING_DEFAULT_MAX_IMAGES
from django.utils.translation import gettext_lazy as _

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
    paginate_by = 2

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
    form_class = ListingForm
    template_name = "listings/html/templates/create.html"
    extra_context = {'submit_url': reverse_lazy("listings:create")}

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        # instantiate a new ImageSet object for this new listing.
        # add it to initial values for the listing form.
        imageset = ImageSet.objects.create(user=request.user)
        self.initial = {'imageset': imageset}
        return super().get(request, *args, **kwargs)

    def form_valid(self, form: ListingForm) -> HttpResponse:
        form.instance.user = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(reverse_lazy("listings:detail", args=[self.object.id]))


class ListingAddImages(LoginRequiredMixin, ListingBase, views.UpdateView):
    template_name = "listings/html/templates/add_images.html"
    extra_context = {}
    fields = ["posted"]
    

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
    success_message = _("Listing updated.")
    
    def get_success_url(self) -> str:
        return reverse_lazy("listings:detail", args=[self.object.id])
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
            Update and create use the same template, distinguished only
            by the form POST url, which is added to the template context here.
        """
        kwargs["update_url"] = reverse_lazy("listings:update", args=[self.object.id])
        return super().get_context_data(**kwargs)


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