from .models import Image, ImageSet
from typing import Any, Iterable, Dict
from django.template.loader import render_to_string
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.core.exceptions import BadRequest
import django.views.generic as views
from django.views.decorators.http import require_POST, require_GET
from .forms import ImageUploadForm, ImageFetchForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class ImageUploader():
    def __init__(self, max_uploads: int = 10, allow_multiple: bool = True, **kwargs: Any) -> None:
        self._max_uploads = max_uploads
        self._allow_multiple = allow_multiple
        self._imageset = ImageSet.objects.create()
        self._main_template = "images/html/includes/main.html"
        self._response_template = "images/html/includes/upload_response.html"
        self._imageuploadform = ImageUploadForm
        super().__init__()

    def get_images(self) -> Iterable[Image]:
        return self._imageset.images.all()

    @property
    def main_template(self) -> str:
        return self._main_template
    
    @property
    def response_template(self) -> str:
        return self._response_template

    @property
    def imageset(self) -> ImageSet:
        return self._imageset
    
    @property
    def max_uploads(self) -> int:
        return self._max_uploads
    
    @property
    def allow_multiple(self) -> bool:
        return self._allow_multiple

    def get_form_html(
            self, 
            request: HttpRequest,
            upload_form: ImageUploadForm = ImageUploadForm,
            url_form: ImageFetchForm = ImageFetchForm
            ) -> str:
        return render_to_string(
            template_name=self.main_template, 
            context= {
                'max_uploads': self._max_uploads, 
                'allow_multiple': self._allow_multiple,
                'images': self.get_images(),
                'upload_form': upload_form,
                'url_form': url_form
            }, 
            request=request
        )
    
    def _dispatch_html(
                self, 
                request, 
                instance = None,
                upload_form: ImageUploadForm = ImageUploadForm,
                url_form: ImageFetchForm = ImageFetchForm
            ):
        if instance:
            try:
                # doesn't change anything if instance is already a list
                images = list(instance)
            except TypeError:
                # converts to list if it wasn't already.
                images = [instance]
        else:
            images = None

        return HttpResponse(
            render_to_string(
                template_name=self.response_template,
                context={
                    'images': images, 
                    'max_uploads': self.max_uploads, 
                    'allow_multiple': self.allow_multiple,
                    'upload_form': upload_form,
                    'url_form': url_form
                }
            )
        )


class HXBase:
    """
        Only allows HTMX requests through; redirects all others.
    """
    def dispatch(self, request, *args, **kwargs):
        if "Hx-Request" not in request.headers:
            return HttpResponseRedirect(reverse_lazy("base:index"))
        return super().dispatch(request, *args, **kwargs)


class HXUploadCounter:
    def dispatch(self, request, *args, **kwargs):
        max_uploads = request.headers.get("Hx-Max-Uploads", None)
        multi = request.headers.get("Hx-Allow-Multiple", True)
        imageset = request.headers.get("Hx-Imageset", None)
        context_dict = {
                "Hx_Max_Uploads": max_uploads, 
                "Hx_Allow_Multiple": multi, 
                "Hx_Imageset": imageset
            }
        if self.extra_context:
            self.extra_context.update(context_dict)
        else:
            self.extra_context = context_dict
        
        return super().dispatch(request, *args, **kwargs)


class HX_Upload(LoginRequiredMixin, HXUploadCounter, HXBase, views.CreateView):
    model = Image
    form_class = ImageUploadForm
    template_name = "images/html/includes/upload_response.html"

    def form_valid(self, form: ImageUploadForm) -> HttpResponse:
        form.instance.uploaded_by = self.request.user
        
        return super().form_valid(form)


class HX_LoadForm(HXUploadCounter, HXBase, views.TemplateView):
    template_name = "images/html/includes/upload_response.html"
    extra_context = {
        "upload_form" : ImageUploadForm,
        "fetch_form": ImageFetchForm,
        "imageset": ImageSet.objects.create()
    }
    def post(self, request:HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.get(*args, **kwargs)
    
    
    
class HX_Detail(views.View):
    pass

class HX_Update(views.View):
    pass

class HX_Destroy(views.View):
    pass