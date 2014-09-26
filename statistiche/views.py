from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.conf import settings

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

from instautomation.utility import get_cursore, check_limite, get_max_id
from .tasks import report_task

import urlparse

MIOIP = settings.IP_LOCALE
CLIENT_SECRET = settings.INSTAGRAM_CLIENT_SECRET
	
@login_required(login_url='/')	
def report_statistico(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
    
	report_task.delay(instance)
	
	return HttpResponse(1221321213)
