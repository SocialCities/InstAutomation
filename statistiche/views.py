from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

import urlparse

MIOIP = "95.238.61.84"

def test_statistica(request):
    instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
    access_token = instance.tokens['access_token']
   
    api = InstagramAPI(
        access_token=access_token,
        client_ips = MIOIP,
        client_secret="e42bb095bdc6494aa351872ea17581ac"
    )
        
    #tra gli utenti che mi seguono, listo quelli con piu' follower
    utenti_che_mi_seguono = api.user_followed_by()
    lista_utenti = utenti_che_mi_seguono[0]
    
    simply_user_obj_list = []
    
    for utente in lista_utenti:
		try:
			check_limite(api)
			user_id = utente.id		
			utente_obj = api.user(user_id)
			username = utente_obj.username
			numero_follower = utente_obj.counts['followed_by']
			#print username + " - seguito da: " + str(numero_follower)
			
			utente.num_follower = numero_follower
			simply_user_obj_list.append(utente)
		except:
			pass
		
    cursore = get_cursore(utenti_che_mi_seguono)
    
    while cursore is not None:
		
		follow_ricorsione = api.user_followed_by(cursor = cursore)		
		utenti_ricorsione = follow_ricorsione[0]
		
		for utente_ricorsione in utenti_ricorsione:
			try:
				check_limite(api)
				user_id = utente_ricorsione.id
				utente_obj = api.user(user_id)
				username = utente_obj.username
				numero_follower = utente_obj.counts['followed_by']
				#print username + " - seguito da: " + str(numero_follower)
				
				utente_ricorsione.num_follower = numero_follower
				simply_user_obj_list.append(utente_ricorsione)				
			except:
				pass
		
		cursore = get_cursore(follow_ricorsione)		   	
	

    aaaa = sorted(simply_user_obj_list, key = lambda user_obj: user_obj.num_follower, reverse=True)
    for user_sorted in aaaa:
		print user_sorted.username + " " + str(user_sorted.num_follower)
    return HttpResponse('access') 
    
    
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

def check_limite(api):
	x_ratelimit_remaining = api.x_ratelimit_remaining
	if (x_ratelimit_remaining < 10) and (x_ratelimit_remaining is not None):
		time.sleep(3600)

