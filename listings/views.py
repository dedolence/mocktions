from django.db.models.query import QuerySet
from django.shortcuts import render
import django.views.generic as views 
from listings.models import Listing
from django.db.models import QuerySet
from typing import Any, Dict, List, Sequence
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from listings.forms import ListingForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from images.models import ImageSet
from globals import LISTING_DEFAULT_MAX_IMAGES
from django.utils.translation import gettext_lazy as _
from images.uploader import fetch_image
from django.utils import lorem_ipsum
import random


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
        HX_ prefix indicates this view is an AJAX call using HTMX in the template.
        To insert a list of listings, add
        {% include 'listings/html/includes/main.html with list_by=user|all %}
        to any template. The template will make an AJAX HTMX call to this view
        which returns HTML that gets swapped into the DOM.
    """
    allow_empty = True
    context_object_name = "listings"    # the context variable name in templates
    template_name = "listings/html/templates/list_small.html"
    paginate_by = 10
    extra_context = {
        
    }

    
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


class ListingRandomizer(ListingCreate):
    def get_initial(self) -> Dict[str, Any]:
        # get the initial imageset which has already been created 
        initial = super().get_initial()

        initial["title"] = lorem_ipsum.words(2, False).title()

        desc_list = lorem_ipsum.paragraphs(2, False)
        max_length = Listing.description.field.max_length - 1
        initial["description"] = '\n'.join(desc_list)[:max_length]

        max_digits = Listing.starting_bid.field.max_digits
        max_bid = int("9" + ("9" * (max_digits-1)))
        initial["starting_bid"] = random.randint(1, max_bid)/100

        categories = Listing.category.field.choices
        initial["category"] = random.choice(categories)[0]

        imageset = self.initial["imageset"]
        min_images = imageset.min_size
        max_images = imageset.max_size
        for i in range(random.randint(min_images, max_images)):
            fetch_image(self.request.user, self.initial["imageset"])

        return initial


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