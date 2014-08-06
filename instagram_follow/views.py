from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

from celery.task.control import revoke
from celery.result import AsyncResult	
from .tasks import how_i_met_your_follower, avvia_task_pulizia_follower
from .forms import RivaliForm
from .models import UtentiRivali, WhitelistUtenti, FollowTaskStatus, BlacklistUtenti

import urlparse
import time

@login_required(login_url='/')
def prendi_follower(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	token = instance.tokens['access_token']	
	
	check_esistenza_task = FollowTaskStatus.objects.filter(utente = instance, completato = False).exists()
	
	if check_esistenza_task:
		return HttpResponseRedirect('/access')
	else:
		result = how_i_met_your_follower.delay(token, instance)
		
		id_task = result.task_id	
		ts = FollowTaskStatus(task_id =  id_task, completato = False, utente = instance)
		ts.save()	   
		
		return HttpResponseRedirect('/access') 	

@login_required(login_url='/')
def ferma_follow(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	ts = FollowTaskStatus.objects.get(utente = instance, completato = False)
	id_task = ts.task_id
	revoke(id_task, terminate=True)	
	
	return HttpResponseRedirect('/access')  
	
	
@login_required(login_url='/')
def avvia_pulizia_follower(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	token = instance.tokens['access_token']	
	
	check_esistenza_task_non_completati = FollowTaskStatus.objects.filter(utente = instance, completato = False).exists()
	
	esistenza_user_da_unfolloware = BlacklistUtenti.objects.filter(utente = instance, unfollowato = False).exists()
	
	if (check_esistenza_task_non_completati is False) and (esistenza_user_da_unfolloware):
		avvia_task_pulizia_follower.delay(token, instance)
		return HttpResponseRedirect('/access') 
	
	return HttpResponseRedirect('/access') 			


@login_required(login_url='/')
def aggiungi_competitor(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	rivale_form = RivaliForm(request.POST)
		
	if rivale_form.is_valid():
		username = rivale_form.cleaned_data['username']
		id_utente = rivale_form.cleaned_data['id_utente']
		nuovo_rivale = UtentiRivali(username = username, id_utente = id_utente, utente = instance)
		nuovo_rivale.save()
						
	return HttpResponseRedirect('/access')         
 
        
@login_required(login_url='/')    
def follower_whitelist(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	
	token = instance.tokens['access_token']	
	
	api = InstagramAPI(
        access_token = token,
        client_ips = "95.238.61.84",
        client_secret = "e42bb095bdc6494aa351872ea17581ac"
	)
    
	followed_by_obj = api.user_follows()
	
	utenti = followed_by_obj[0]
	for utente in utenti:
		esistenza_nuovo_user = WhitelistUtenti.objects.filter(username = utente.username, id_utente = utente.id, utente = instance).exists()
		if esistenza_nuovo_user is False:
			nuovo_user_whitelist = WhitelistUtenti(username = utente.username, id_utente = utente.id, utente = instance)
			nuovo_user_whitelist.save()		

	cursore = get_cursore(followed_by_obj)
	
	while cursore is not None:
		
		follow_ricorsione = api.user_follows(cursor = cursore)
		
		utenti_ricorsione = follow_ricorsione[0]
		for utente_ricorsione in utenti_ricorsione:
			esistenza_nuovo_user_ricorsione = WhitelistUtenti.objects.filter(username = utente_ricorsione.username, id_utente = utente_ricorsione.id, utente = instance).exists()
			if esistenza_nuovo_user_ricorsione is False:
				nuovo_user_whitelist2 = WhitelistUtenti(username = utente_ricorsione.username, id_utente = utente_ricorsione.id, utente = instance)
				nuovo_user_whitelist2.save()
						
		cursore = get_cursore(follow_ricorsione)    	
	
	return HttpResponseRedirect('/access') 


def get_cursore(followed_obj):	
	blocco_pagination = followed_obj[1]
	
	if blocco_pagination is None:
		return None
	else:
		o = urlparse.urlparse(blocco_pagination)
		query = o.query
		query_parsed = urlparse.parse_qs(query)
		cursore = query_parsed['cursor'][0]
		return cursore


def porco_giuda(request):
    instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
    access_token = instance.tokens['access_token']
    
    ts = FollowTaskStatus.objects.filter(utente = instance, completato = False)
    for tas in ts:
		id_task = tas.task_id
		revoke(id_task, terminate=True)	   
   
    #api = InstagramAPI(
     #   access_token=access_token,
     #   client_ips="95.238.61.84",
    #    client_secret="e42bb095bdc6494aa351872ea17581ac"
   # )
    
    #x = api.follow_user(user_id = '42002034')       
    #relation_obj = x[0]
    #print relation_obj.outgoing_status

    
    return HttpResponse('stop')
