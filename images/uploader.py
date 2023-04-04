from .models import Image, ImageSet
from typing import Any, Iterable, Dict, Optional
from django.template.loader import render_to_string
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
import django.views.generic as views
from .forms import ImageUploadForm, ImageFetchForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class HXBase:
    """
        Only allows HTMX requests through; redirects all others.
        Includes a method for rendering upload_response.html which is
        the basis for most HTMX transactions as it refreshes the forms
        and appends any new images to the page.
    """
    def dispatch(self, request, *args, **kwargs):
        if "Hx-Request" not in request.headers:
            return HttpResponseRedirect(reverse_lazy("base:index"))
        return super().dispatch(request, *args, **kwargs)
    

    def render_hx_response(
            self, 
            request: HttpRequest, 
            imageset: Optional[ImageSet],
            upload_form: Optional[ImageUploadForm] = ImageUploadForm(),
            fetch_form: Optional[ImageFetchForm] = ImageFetchForm()):
        return HttpResponse(
            render_to_string(
                template_name="images/html/includes/upload_response.html",
                context={
                    'upload_form': upload_form,
                    'fetch_form': fetch_form,
                    'imageset': imageset
                },
                request=request
            )
        )


class HX_Upload(LoginRequiredMixin, HXBase, views.CreateView):
    model = Image
    form_class = ImageUploadForm

    def form_valid(self, form: ImageUploadForm) -> HttpResponse:
        form.instance.uploaded_by = self.request.user
        self.object = form.save()

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        form = self.get_form()
        imageset = ImageSet.objects.get(pk=request.POST.get('imageset'))

        if form.is_valid():
            form.instance.uploaded_by = self.request.user 
            self.object = form.save()
            upload_form = ImageUploadForm(initial={'imageset': imageset.id})
        else:
            upload_form = form

        return self.render_hx_response(request, imageset, upload_form)


class HX_LoadForm(HXBase, views.TemplateView):
    """
        Generates a new Imageset object and provides it, along with the image upload form.
        Subsequent image uploads will be linked to the imageset for tracking maximum 
        allowable uploads per post, user, etc..
    """
    template_name = "images/html/includes/upload_response.html"

    def post(self, request:HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.get(*args, **kwargs)
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        max_size = int(kwargs['imageset_size'])
        imageset = ImageSet.objects.create(max_size=max_size, user=self.request.user)
        self.extra_context = {
            "upload_form": ImageUploadForm(initial={'imageset': imageset}),
            "fetch_form": ImageFetchForm(initial={'imageset': imageset}),
            "imageset": imageset
        }
        return super().get(request, *args, **kwargs)
    
    
    
class HX_Detail(views.View):
    pass

class HX_Update(views.View):
    pass

class HX_Destroy(views.View):
    pass