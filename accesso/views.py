from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.views.generic import View
from django.conf import settings

from instagram_like.models import ListaTag, BlacklistFoto
from instagram_like.forms import TagForm
from instagram_follow.models import UtentiRivali
from instagram_follow.forms import CercaCompetitorForm
from .models import trackStats, TaskStatus

from celery.result import AsyncResult
from celery.task.control import revoke

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

MIOIP = settings.IP_LOCALE
	
def index(request):	
	return render_to_response('instalogin.html', context_instance=RequestContext(request))
	
def uscita(request):
    logout(request)
    return HttpResponseRedirect('/access') 	

def access(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']
	
	esistenza_track = trackStats.objects.filter(utente = instance).exists()
    
	if esistenza_track:
		return HttpResponseRedirect('/home')
	else:
				
		api = InstagramAPI(
				access_token = access_token,
				client_ips = MIOIP,
				client_secret = "e42bb095bdc6494aa351872ea17581ac"
		)
		
		informazioni = api.user()			
		followed_by = informazioni.counts['followed_by']
		nuove_stats = trackStats(utente = instance, follower_iniziali = followed_by)
		nuove_stats.save()
		
		return HttpResponseRedirect('/home')   
		
class beta_home(View):
    template_name = 'beta_home.html'
    codice_beta = "pota"

    def dispatch(self, *args, **kwargs):
        return super(beta_home, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
	
    def post(self, request, *args, **kwargs):   
		beta_code = request.POST['beta_code'] 
		if beta_code == self.codice_beta: 
			request.session['in_beta'] = True   
			return HttpResponseRedirect('/home')
		else:
			return HttpResponseRedirect('/beta/')			
		
@login_required(login_url='/')
def home_page(request):	
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']	
	template = loader.get_template('home_page.html')
	
	cerca_competitor_form = CercaCompetitorForm()
	cerca_competitor_form.fields['username'].label = 'Cerca un competitor'
	
	rivali = UtentiRivali.objects.filter(utente = instance) 	
	
	lista_tag = ListaTag.objects.filter(utente = instance) 	
	tag_form = TagForm()
	
	status_obj_attivi = TaskStatus.objects.filter(utente = instance, completato = False).exists()

	api = InstagramAPI(
			access_token = access_token,
			client_ips = MIOIP,
			client_secret = "e42bb095bdc6494aa351872ea17581ac"
	)	
	
	context = RequestContext(request, {
		'rivali' : rivali,
		'competitor_form' : cerca_competitor_form,
		'lista_tag' : lista_tag,
		'tag_form' : tag_form,
		'status_obj_attivi' : status_obj_attivi,
	})
		
	return HttpResponse(template.render(context))	
	
@login_required(login_url='/')
def cerca_competitor(request):	
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']	
	
	cerca_competitor_form = CercaCompetitorForm(request.GET)
	if cerca_competitor_form.is_valid():
		nome_da_cercare = cerca_competitor_form.cleaned_data['username']
	
	template = loader.get_template('home_page_rivali.html')
	
	cerca_competitor_form = CercaCompetitorForm()
	cerca_competitor_form.fields['username'].label = 'Cerca un competitor'
	
	rivali = UtentiRivali.objects.filter(utente = instance) 	
	
	lista_tag = ListaTag.objects.filter(utente = instance) 	
	tag_form = TagForm()
	
	status_obj_attivi = TaskStatus.objects.filter(utente = instance, completato = False).exists()
	
	api = InstagramAPI(
			access_token = access_token,
			client_ips = MIOIP,
			client_secret = "e42bb095bdc6494aa351872ea17581ac"
	)	
	
	tutti_nomi = api.user_search(q = nome_da_cercare)	
	
	context = RequestContext(request, {
		'rivali' : rivali,
		'competitor_form' : cerca_competitor_form,
		'lista_tag' : lista_tag,
		'tag_form' : tag_form,
		'tutti_nomi' : tutti_nomi,
		'status_obj_attivi' : status_obj_attivi,
	})
		
	return HttpResponse(template.render(context))	

@login_required(login_url='/')
def ferma_task(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	task_attivi = TaskStatus.objects.filter(completato = False, utente = instance).exists()
	
	if task_attivi:
		task_attivo = TaskStatus.objects.get(completato = False, utente = instance)
		task_id = task_attivo.task_id
		task_attivo.completato = True
		task_attivo.save()
		revoke(task_id, terminate=True, signal="KILL")
		
	return HttpResponseRedirect('/home')

@login_required(login_url='/')
def avvia_task(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	nuovo_task = TaskStatus(completato = False, utente = instance)
	nuovo_task.save()
	
	print 'aaaaaaaaaaa'
		
	return HttpResponseRedirect('/home')
