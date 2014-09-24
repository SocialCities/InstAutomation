from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

from .models import ListaTag, BlacklistFoto
from .forms import TagForm

from celery.task.control import revoke
from celery.result import AsyncResult	
from .tasks import insta_task

MIOIP = settings.IP_LOCALE

@login_required(login_url='/')
def aggiungi_tag(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	tag_form = TagForm(request.POST)
	if tag_form.is_valid():
		testo_tag = tag_form.cleaned_data['keyword']
		nuovo_tag = ListaTag(keyword = testo_tag, utente = instance)
		nuovo_tag.save()
			
		return HttpResponseRedirect('/home')
 



