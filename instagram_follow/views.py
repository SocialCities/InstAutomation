from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

from .models import UtentiRivali, WhitelistUtenti, BlacklistUtenti
from .forms import RivaliForm

import json

from instautomation.utility import get_cursore

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

		mio_username = instance.extra_data['username']
		if username == mio_username:
			return HttpResponse("myself")
		
		api = InstagramAPI(
			access_token = access_token,
			client_ips = MIOIP,
			client_secret = CLIENT_SECRET 
		)
		
		numero_follower = api.user(id_utente).counts['followed_by']
		esistenza = UtentiRivali.objects.filter(username = username, id_utente = id_utente, utente = instance).exists()
		
		if esistenza:
			return HttpResponse("user_exists")
		else:
			nuovo_rivale = UtentiRivali(username = username, id_utente = id_utente, utente = instance, numero_follower = numero_follower)
			nuovo_rivale.save()

			return HttpResponse()    
	
@login_required(login_url='/login')
def rimuovi_competitor(request):	 	
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	
	nome_rivale = request.POST['nome_rivale']

	esisteza_user = UtentiRivali.objects.filter(username = nome_rivale, utente = instance).exists()
	if esisteza_user:
		utente_da_eliminare = UtentiRivali.objects.get(username = nome_rivale, utente = instance)
		utente_da_eliminare.delete()
	
	return HttpResponse()


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


@login_required(login_url='/login')
def cerca_competitor(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	access_token = instance.tokens['access_token']	
	nome_da_cercare = request.POST['keyword']

	api = InstagramAPI(
			access_token = access_token,
			client_ips = MIOIP,
			client_secret = CLIENT_SECRET 
	)	

	tutti_nomi = api.user_search(q = nome_da_cercare, count = 10)

	new_tutti_nomi = []

	for nome in tutti_nomi:
		try:
			followed_by = api.user(nome.id).counts['followed_by']
			nome.followed_by = followed_by
			new_tutti_nomi.append(nome)
		except:
			pass	
		
	new_tutti_nomi = sorted(new_tutti_nomi, key = lambda user_obj: user_obj.followed_by, reverse=True)

	output = {}
	output_full_user = []

	for name in new_tutti_nomi:
		user = {}
		user["username"] = name.username
		user["id"] = name.id
		user["followed_by"] = name.followed_by
		output_full_user.append(user)

	output["users"] = output_full_user

	return HttpResponse(
    	json.dumps(output),
        content_type="application/json"
    )

