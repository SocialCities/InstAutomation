from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.conf import settings

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

from instagram_like.models import ListaTag

from .models import UtentiRivali, WhitelistUtenti, BlacklistUtenti
from .forms import CercaCompetitorForm, RivaliForm

from instautomation.utility import get_cursore

import urlparse

MIOIP = settings.IP_LOCALE
CLIENT_SECRET = settings.INSTAGRAM_CLIENT_SECRET

@login_required(login_url='/login')
def aggiungi_competitor(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	access_token = instance.tokens['access_token']	
	
	rivale_form = RivaliForm(request.POST)
		
	if rivale_form.is_valid():
		username = rivale_form.cleaned_data['username']
		id_utente = rivale_form.cleaned_data['id_utente']
		
		api = InstagramAPI(
			access_token = access_token,
			client_ips = MIOIP,
			client_secret = CLIENT_SECRET 
		)
		
		numero_follower = api.user(id_utente).counts['followed_by']
		nuovo_rivale = UtentiRivali(username = username, id_utente = id_utente, utente = instance, numero_follower = numero_follower)
		nuovo_rivale.save()
						
	return HttpResponseRedirect('/')     
	
@login_required(login_url='/login')
def rimuovi_competitor(request):	 	
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	
	nome_rivale = request.POST['nome_rivale']
	
	utente_da_eliminare = UtentiRivali.objects.get(username = nome_rivale, utente = instance)
	utente_da_eliminare.delete()
	
	return HttpResponseRedirect('/')


def update_whitelist(api, instance):
	cursore = None
	uscita = False
	
	while uscita is False:
		followed_by_obj = api.user_follows(cursor = cursore)
		utenti = followed_by_obj[0]
		
		for utente in utenti:
			esistenza_nuovo_user = WhitelistUtenti.objects.filter(id_utente = utente.id, utente = instance).exists()
			esistenza_in_black = BlacklistUtenti.objects.filter(id_utente = utente.id, utente = instance).exists()			
			
			if (esistenza_nuovo_user is False) and (esistenza_in_black is False):
				nuovo_user_whitelist = WhitelistUtenti(username = utente.username, id_utente = utente.id, utente = instance)
				nuovo_user_whitelist.save()	
		
		cursore, uscita = get_cursore(followed_by_obj)

