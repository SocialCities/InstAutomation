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
	
def index(request):	
	return render_to_response('instalogin.html', context_instance=RequestContext(request))
	
def uscita(request):
    logout(request)
    return HttpResponseRedirect('/access') 	
    
def get_informazioni_basilari(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']		
	tags = ListaTag.objects.filter(utente = instance)	
		
	rivali = UtentiRivali.objects.filter(utente = instance) 
		
	check_esistenza_task = LikeTaskStatus.objects.filter(utente = instance, completato = False).exists()	
		
	if check_esistenza_task:
		task_non_finiti = LikeTaskStatus.objects.filter(utente = instance, completato = False)
		for task in task_non_finiti:
			id_task = task.task_id
			res = AsyncResult(id_task)
			check_res = res.ready() 	
			if check_res:
				task.completato = True
				task.save()
				check_esistenza_task = False

	check_esistenza_follow_task = FollowTaskStatus.objects.filter(utente = instance, completato = False).exists()

	if check_esistenza_follow_task:
		task_follow_non_finiti = FollowTaskStatus.objects.filter(utente = instance, completato = False)
		for task in task_follow_non_finiti:
			id_task = task.task_id
			res = AsyncResult(id_task)
			check_res = res.ready() 	
			if check_res:
				task.completato = True
				task.save()
				check_esistenza_follow_task = False

	booleano_controllo_pulizia = False	
	esistenza_user_da_unfolloware = BlacklistUtenti.objects.filter(utente = instance, unfollowato = False).exists()	
	if (check_esistenza_follow_task is False) and (esistenza_user_da_unfolloware):
		booleano_controllo_pulizia = True
		
	tag_form = TagForm()
	tag_form.fields['keyword'].label = 'Inserisci un nuovo hashtag'
		
	cerca_competitor_form = CercaCompetitorForm()
	cerca_competitor_form.fields['username'].label = 'Cerca un competitor'
	
	whitelist_utenti = WhitelistUtenti.objects.filter(utente = instance)
		
	return tags, check_esistenza_task, check_esistenza_follow_task, booleano_controllo_pulizia, tag_form, rivali, cerca_competitor_form, access_token, whitelist_utenti   
						
@login_required(login_url='/')
def gestione_accesso(request):
	
	tags, check_esistenza_task, check_esistenza_follow_task, booleano_controllo_pulizia, tag_form, rivali, cerca_competitor_form, access_token, whitelist_utenti = get_informazioni_basilari(request)
					
	template = loader.get_template('home.html')
	context = RequestContext(request, {
		'tags': tags,
		'check_esistenza_task' : check_esistenza_task,
		'tag_form' : tag_form,
		'rivali' : rivali,
		'cerca_competitor_form' : cerca_competitor_form,
		'whitelist_utenti' : whitelist_utenti,
		'check_esistenza_follow_task' : check_esistenza_follow_task,
		'booleano_controllo_pulizia' : booleano_controllo_pulizia,
	})
		
	return HttpResponse(template.render(context))			

@login_required(login_url='/')
def cerca_competitor(request):

	tags, check_esistenza_task, check_esistenza_follow_task, booleano_controllo_pulizia, tag_form, rivali, cerca_competitor_form, access_token, whitelist_utenti = get_informazioni_basilari(request)
	
	cerca_competitor_form = CercaCompetitorForm(request.GET)
	if cerca_competitor_form.is_valid():
		nome_da_cercare = cerca_competitor_form.cleaned_data['username']
	#else:
	#	return HttpResponse('no')
	
	api = InstagramAPI(
        access_token=access_token,
        client_ips="82.106.24.34",
        client_secret="e42bb095bdc6494aa351872ea17581ac"
    )
    
	rivali_form = RivaliForm()
	
	tutti_nomi = api.user_search(q = nome_da_cercare)	
					
	template = loader.get_template('home2.html')
	context = RequestContext(request, {
		'tags': tags,
		'check_esistenza_task' : check_esistenza_task,
		'tag_form' : tag_form,
		'rivali' : rivali,
		'cerca_competitor_form' : cerca_competitor_form,
		'tutti_nomi': tutti_nomi,
		'rivali_form' : rivali_form,
		'whitelist_utenti' : whitelist_utenti,
		'check_esistenza_follow_task': check_esistenza_follow_task,
		'booleano_controllo_pulizia' : booleano_controllo_pulizia,
	})
		
	return HttpResponse(template.render(context))		
		
	

