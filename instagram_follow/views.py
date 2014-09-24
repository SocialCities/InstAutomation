from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.conf import settings

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

from instagram_like.models import ListaTag

from .models import UtentiRivali, WhitelistUtenti
from .forms import CercaCompetitorForm, RivaliForm
from .tasks import how_i_met_your_follower

from InstaTrezzi.utility import get_cursore

import urlparse

MIOIP = settings.IP_LOCALE

@login_required(login_url='/')
def aggiungi_competitor(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	rivale_form = RivaliForm(request.POST)
		
	if rivale_form.is_valid():
		username = rivale_form.cleaned_data['username']
		id_utente = rivale_form.cleaned_data['id_utente']
		nuovo_rivale = UtentiRivali(username = username, id_utente = id_utente, utente = instance)
		nuovo_rivale.save()
						
	return HttpResponseRedirect('/home')      	


#
#def update_whitelist(api, instance):
	
#	followed_by_obj = api.user_follows()
#	utenti = followed_by_obj[0]
	
#	for utente in utenti:
#		esistenza_nuovo_user = WhitelistUtenti.objects.filter(username = utente.username, id_utente = utente.id, utente = instance).exists()
#		if esistenza_nuovo_user is False:
#			nuovo_user_whitelist = WhitelistUtenti(username = utente.username, id_utente = utente.id, utente = instance)
#			nuovo_user_whitelist.save()		

#	cursore = get_cursore(followed_by_obj)	
	
#	while cursore is not None:		
#		follow_ricorsione = api.user_follows(cursor = cursore)
#		
#		utenti_ricorsione = follow_ricorsione[0]
#		for utente_ricorsione in utenti_ricorsione:
#			esistenza_nuovo_user_ricorsione = WhitelistUtenti.objects.filter(username = utente_ricorsione.username, id_utente = utente_ricorsione.id, utente = instance).exists()
#			if esistenza_nuovo_user_ricorsione is False:
#				nuovo_user_whitelist2 = WhitelistUtenti(username = utente_ricorsione.username, id_utente = utente_ricorsione.id, utente = instance)
#				nuovo_user_whitelist2.save()
						
#		cursore = get_cursore(follow_ricorsione)  	
	
#@login_required(login_url='/')
#def prendi_follower(request):
#	rivale_form = RivaliForm(request.POST)
	
#	if rivale_form.is_valid():
#		username_rivale = rivale_form.cleaned_data['username']
#		id_utente = rivale_form.cleaned_data['id_utente']
	
#		instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
#		token = instance.tokens['access_token']	
	
#		api = InstagramAPI(
#			access_token = token,
#			client_ips = MIOIP,
#			client_secret = "e42bb095bdc6494aa351872ea17581ac"
#		)
	
#		update_whitelist(api, instance)
				
#		result = how_i_met_your_follower.delay(token, instance, id_utente)
		
#		id_task = result.task_id	
#		ts = FollowTaskStatus(task_id =  id_task, completato = False, utente = instance)
#		ts.save()	   
			
#		return HttpResponseRedirect('/home')	
#	else:
#		return HttpResponseBadRequest()
