from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from social_auth.models import UserSocialAuth
from instagram_like.models import ListaTag, BlacklistFoto, LikeTaskStatus
from instagram_like.forms import TagForm
from instagram_follow.models import UtentiRivali, WhitelistUtenti, FollowTaskStatus, BlacklistUtenti
from instagram_follow.forms import CercaCompetitorForm, RivaliForm

from celery.result import AsyncResult

from instagram.client import InstagramAPI

#Decorator
def task_non_completati(function):
  def wrap(request, *args, **kwargs):
		
        follow_task_attivi = FollowTaskStatus.objects.filter(completato = False).exists()
        like_task_attivi = LikeTaskStatus.objects.filter(completato = False).exists()
        print follow_task_attivi
        print like_task_attivi

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

@login_required(login_url='/')
def task_esistente(request):		
	return render_to_response('task_esistente.html')

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
