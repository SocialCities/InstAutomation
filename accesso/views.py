from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.generic import View
from django.utils.decorators import method_decorator

from social_auth.models import UserSocialAuth
from instagram_like.models import ListaTag, BlacklistFoto, LikeTaskStatus
from instagram_like.forms import TagForm
from instagram_follow.models import UtentiRivali, WhitelistUtenti, FollowTaskStatus, BlacklistUtenti
from instagram_follow.forms import CercaCompetitorForm, RivaliForm

from celery.result import AsyncResult
from celery.task.control import revoke

from instagram.client import InstagramAPI

#Decorator
def task_non_completati(function):
  def wrap(request, *args, **kwargs):
        instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	  	
        follow_task_attivi = FollowTaskStatus.objects.filter(completato = False, utente = instance).exists()
        like_task_attivi = LikeTaskStatus.objects.filter(completato = False, utente = instance).exists()

        if (follow_task_attivi is True) or (like_task_attivi is True):
			
			return HttpResponseRedirect('/task_esistente')
        else:
            return function(request, *args, **kwargs)

  wrap.__doc__=function.__doc__
  wrap.__name__=function.__name__
  return wrap
		
def index(request):	
	return render_to_response('instalogin.html', context_instance=RequestContext(request))
	
def uscita(request):
    logout(request)
    return HttpResponseRedirect('/access') 	

def access(request):
    return HttpResponseRedirect('/home') 	    

@login_required(login_url='/')
@task_non_completati
def home_page(request):	
	return render_to_response('index.html')	

class task_esistente(View):
    template_name = 'task_esistente.html'

    @method_decorator(login_required(login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(task_esistente, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
	
    def post(self, request, *args, **kwargs):
		instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	  	
		follow_task_attivi = FollowTaskStatus.objects.filter(completato = False, utente = instance).exists()
		like_task_attivi = LikeTaskStatus.objects.filter(completato = False, utente = instance).exists()
		
		if follow_task_attivi:
			task_attivo = FollowTaskStatus.objects.get(completato = False, utente = instance)
			task_id = task_attivo.task_id
			task_attivo.completato = True
			task_attivo.save()
			revoke(task_id, terminate=True, signal="KILL")	
			
		if like_task_attivi:
			like_attivo = LikeTaskStatus.objects.get(completato = False, utente = instance)
			task_id = like_attivo.task_id
			like_attivo.completato = True
			like_attivo.save()
			revoke(task_id, terminate=True, signal="KILL")	
        
		return HttpResponseRedirect('/home')

@login_required(login_url='/')
def follow_home(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']	
	template = loader.get_template('follow_home.html')
	
	rivali = UtentiRivali.objects.filter(utente = instance) 	
	cerca_competitor_form = CercaCompetitorForm()
	cerca_competitor_form.fields['username'].label = 'Cerca un competitor'
	
	context = RequestContext(request, {
		'rivali' : rivali,
		'form' : cerca_competitor_form,
	})
		
	return HttpResponse(template.render(context))	
	
@login_required(login_url='/')
def cerca_competitor(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']	
	
	cerca_competitor_form = CercaCompetitorForm(request.GET)
	if cerca_competitor_form.is_valid():
		nome_da_cercare = cerca_competitor_form.cleaned_data['username']
	
	api = InstagramAPI(
        access_token=access_token,
        client_ips="82.106.24.34",
        client_secret="e42bb095bdc6494aa351872ea17581ac"
    )
    
	rivali = UtentiRivali.objects.filter(utente = instance) 	
	cerca_competitor_form = CercaCompetitorForm()
	cerca_competitor_form.fields['username'].label = 'Cerca un competitor'
	
	tutti_nomi = api.user_search(q = nome_da_cercare)	
					
	template = loader.get_template('follow_home_ricerca.html')
	context = RequestContext(request, {
		'tutti_nomi': tutti_nomi,		
		'rivali' : rivali,
		'form' : cerca_competitor_form,
	})
		
	return HttpResponse(template.render(context))
	

@login_required(login_url='/')
def aggiungi_competitor(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	rivale_form = RivaliForm(request.POST)
		
	if rivale_form.is_valid():
		username = rivale_form.cleaned_data['username']
		id_utente = rivale_form.cleaned_data['id_utente']
		nuovo_rivale = UtentiRivali(username = username, id_utente = id_utente, utente = instance)
		nuovo_rivale.save()
						
	return HttpResponseRedirect('/follow')      	
