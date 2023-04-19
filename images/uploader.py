from .models import Image, ImageSet
from typing import Any, Iterable, Dict, Optional, List
from django.template.loader import render_to_string
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
import django.views.generic as views
from .forms import ImageUploadForm, ImageFetchForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files import File
from urllib import request as requests


"""
    Usage:
    To create a new imageset:
    {% include 'images/html/includes/main.html' with max_uploads=n %}

    To load and edit an existing imageset:
    {% include 'images/html/includes/main.html' with imageset=n %}
"""

class HXImageBase:
    """
        Only allows HTMX requests through; redirects all others.
        Includes a method for rendering upload_response.html which is
        the basis for most HTMX transactions as it refreshes the forms
        and appends any new images to the page.
    """
    def dispatch(self, request, *args, **kwargs):
        if "Hx-Request" not in request.headers:
            return HttpResponseRedirect(reverse_lazy("base:index"))
        
        if not request.user.is_authenticated:
            return self.login_redirect(request)

        return super().dispatch(request, *args, **kwargs)
    
    def login_redirect(self, request):
        """
            If user isn't authenticated, provide a redirect to a login form.
        """
        return HttpResponse(
            render_to_string(
                template_name="images/html/includes/login_redirect.html",
                request=request
            )
        )

    def render_hx_response(
            self, 
            request: HttpRequest, 
            imageset: int,
            images: Optional[List[Image]] = None,
            upload_form: Optional[ImageUploadForm] = None,
            fetch_form: Optional[ImageFetchForm] = None,
            ) -> HttpResponse:
        
        # convert single objects to an iterable list
        if images:
            try:
                images = list(images)
            except TypeError:
                images = [images]

        initial = {'imageset': imageset}
        if upload_form is None:
            upload_form = ImageUploadForm(initial=initial)
        if fetch_form is None:
            fetch_form = ImageFetchForm(initial=initial)

        return HttpResponse(
            render_to_string(
                template_name="images/html/includes/upload_response.html",
                context={
                    'upload_form': upload_form,
                    'fetch_form': fetch_form,
                    'images': images,
                    'imageset': imageset
                },
                request=request
            )
        )


def HX_Reorder(request):
    """
        Important: status 204 is required to indicate to HTMX that no
        DOM changes should be made.
    """
    image_list = request.POST.getlist('image_list')
    for i, id in enumerate(image_list):
        img = Image.objects.get(pk=id)
        img.order = i 
        img.save()
    return HttpResponse(content="", status=204)


class HX_Fetch(LoginRequiredMixin, HXImageBase, views.CreateView):
    """ For saving an Image instance from a provided URL."""
    model = Image
    form_class = ImageFetchForm

    def form_valid(self, form: ImageFetchForm) -> HttpResponse:
        imageset = ImageSet.objects.get(pk=self.request.POST.get('imageset'))
        url = form.cleaned_data['url']
        image = Image.objects.create(uploaded_by=self.request.user)
        res = requests.urlretrieve(url)

        name = res[0].split('/')[-1]
        name = name + ".jpg" if ".jpg" not in name else name

        image.image_field.save(name, File(open(res[0], 'rb')))
        image.imageset = imageset
        image.save()

        self.object = image
        return self.render_hx_response(self.request, imageset, self.object)
    
    def form_invalid(self, form: ImageFetchForm) -> HttpResponse:
        imageset = ImageSet.objects.get(pk=self.request.POST.get('imageset'))
        return self.render_hx_response(self.request, imageset, self.object)


class HX_Upload(LoginRequiredMixin, HXImageBase, views.CreateView):
    model = Image
    form_class = ImageUploadForm

    def form_valid(self, form: ImageUploadForm) -> HttpResponse:
        imageset = ImageSet.objects.get(pk=self.request.POST.get('imageset'))
        form.instance.uploaded_by = self.request.user 
        self.object = form.save()
        return self.render_hx_response(self.request, imageset, self.object)
    
    def form_invalid(self, form: ImageUploadForm) -> HttpResponse:
        imageset = ImageSet.objects.get(pk=self.request.POST.get('imageset'))
        return self.render_hx_response(self.request, imageset, self.object, upload_form=form)




class HX_LoadForm(HXImageBase, views.TemplateView):
    """
        Either takes the pk of an existing imageset or generates a new one.
        All images subsequently uploaded will be related to the imageset.

        TODO: take out the hard-coded max-size default.
    """
    template_name = "images/html/includes/upload_response.html"

    def post(self, request:HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.get(*args, **kwargs)
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # check for existing imageset, create a new one as necessary
        try: 
            pk = kwargs['imageset_id']
            imageset = ImageSet.objects.get(pk=pk)
        except KeyError:
            max_size = int(request.GET.get('size', 10))
            imageset = ImageSet.objects.create(max_size=max_size, user=self.request.user)
        
        return self.render_hx_response(request, imageset, imageset.images.all())
    

class HX_Update(views.UpdateView):
    """
        Updates the image alt text.
    """
    model = Image
    fields = ["alt"]

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse(
            render_to_string(
                template_name="images/html/templates/toast_message.html",
                context={
                    'message': 'Image updated.'
                }
            ), 
            #headers={'HX-Trigger': "displayToast"},
        )
        


class HX_Destroy(LoginRequiredMixin, views.DeleteView):
    model = Image
    
    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        obj = self.get_object()
        image_id = obj.id
        obj.delete()
        return HttpResponse(
            render_to_string(
                template_name="images/html/templates/delete.html",
                context={
                    'image_id': image_id,
                    'message': 'Image deleted.'
                }
            ), 
            headers={
                'HX-Trigger': "displayToast",
            },
        )