from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

from .models import UtentiRivali, WhitelistUtenti, FollowTaskStatus
from .forms import CercaCompetitorForm, RivaliForm

from .tasks import how_i_met_your_follower

import urlparse

MIOIP = "79.47.52.179"

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

@login_required(login_url='/')
def cerca_competitor(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']	
	
	cerca_competitor_form = CercaCompetitorForm(request.GET)
	if cerca_competitor_form.is_valid():
		nome_da_cercare = cerca_competitor_form.cleaned_data['username']
	
	api = InstagramAPI(
        access_token = access_token,
        client_ips = MIOIP,
        client_secret = "e42bb095bdc6494aa351872ea17581ac"
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

def update_whitelist(api, instance):
	
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
	
@login_required(login_url='/')
def prendi_follower(request):
	rivale_form = RivaliForm(request.POST)
	
	if rivale_form.is_valid():
		username_rivale = rivale_form.cleaned_data['username']
		id_utente = rivale_form.cleaned_data['id_utente']
	
		instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
		token = instance.tokens['access_token']	
	
		api = InstagramAPI(
			access_token = token,
			client_ips = MIOIP,
			client_secret = "e42bb095bdc6494aa351872ea17581ac"
		)
	
		update_whitelist(api, instance)
				
		result = how_i_met_your_follower.delay(token, instance, id_utente)
		
		id_task = result.task_id	
		ts = FollowTaskStatus(task_id =  id_task, completato = False, utente = instance)
		ts.save()	   
			
		return HttpResponseRedirect('/home')	
	else:
		return HttpResponseBadRequest()
		
		
@login_required(login_url='/')
def get_info(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	token = instance.tokens['access_token']	
	
	api = InstagramAPI(
			access_token = token,
			client_ips = MIOIP,
			client_secret = "e42bb095bdc6494aa351872ea17581ac"
	)	
	
	id_utente = request.GET['id']
	informazioni = api.user(id_utente)
	followed_by = informazioni.counts['followed_by']
	stima = followed_by*2*1.05
			
	return HttpResponse(stima)
