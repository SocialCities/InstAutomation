from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

from .models import ListaTag, BlacklistFoto, LikeTaskStatus
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
			
		return HttpResponseRedirect('/like') 
 
@login_required(login_url='/')   
def avvia_like(request):    
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	token = instance.tokens['access_token']
	access_token = token
		
	check_esistenza_task = LikeTaskStatus.objects.filter(utente = instance, completato = False).exists()
	
	if check_esistenza_task:
		return HttpResponseRedirect('/access') 
	else:
		result = insta_task.delay(access_token, instance)
		
		id_task = result.task_id	
		ts = LikeTaskStatus(task_id =  id_task, completato = False, utente = instance)
		ts.save()
	
		return HttpResponseRedirect('/access') 		

@login_required(login_url='/')
def ferma_like(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	ts = LikeTaskStatus.objects.get(utente = instance, completato = False)
	id_task = ts.task_id
	revoke(id_task, terminate=True)	
	
	return HttpResponseRedirect('/access')  



