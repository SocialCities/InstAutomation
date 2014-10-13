from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render
from .tasks import pulsantone_rosso

class pulsantone_view(View):
    template_name = 'pulsantone.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(pulsantone_view, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
	
    def post(self, request, *args, **kwargs):
    	pulsantone_rosso.delay()   
    	return HttpResponse("Panic!")