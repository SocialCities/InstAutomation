from __future__ import absolute_import

from celery import shared_task
from .models import BlacklistUtenti, WhitelistUtenti, FollowTaskStatus
from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI
import time
import urlparse
import logging
logger = logging.getLogger('django')

MIOIP = "79.47.52.179"
    
@shared_task   
def how_i_met_your_follower(access_token, instance, id_rivale):
		
	api = InstagramAPI(
        access_token=access_token,
        client_ips = MIOIP,
        client_secret = "e42bb095bdc6494aa351872ea17581ac"
    )
    
	check_limite(api)
    
	followed_by_obj = api.user_followed_by(id_rivale)
	
	check_limite(api)
	
	mega_lista_utenti = []
    
	utenti = followed_by_obj[0]
	for utente in utenti:
			esistenza_nuovo_user = BlacklistUtenti.objects.filter(username = utente.username, id_utente = utente.id, utente = instance).exists()
			esistenza_in_white = WhitelistUtenti.objects.filter(username = utente.username, id_utente = utente.id, utente = instance).exists()
			
			if (esistenza_nuovo_user is False) and (esistenza_in_white is False):
				
				check_limite(api)			
				mega_lista_utenti.append(utente.id)
				try:
					x = api.follow_user(user_id = utente.id)
				
					nuovo_user_blackilist = BlacklistUtenti(username = utente.username, id_utente = utente.id, utente = instance, unfollowato = False)
					nuovo_user_blackilist.save()
				
					time.sleep(65)
				except:
					logger.error("how_i_met_your_follower", exc_info=True)
					pass
		
	cursore = get_cursore(followed_by_obj)
	
	while cursore is not None:		
		follow_ricorsione = api.user_followed_by(id_rivale, cursor = cursore)
		
		check_limite(api)
		
		utenti_ricorsione = follow_ricorsione[0]
		for utente_ricorsione in utenti_ricorsione:
				esistenza_nuovo_user_ricorsione = BlacklistUtenti.objects.filter(username = utente_ricorsione.username, id_utente = utente_ricorsione.id, utente = instance).exists()
				esistenza_in_white_ricorsione = WhitelistUtenti.objects.filter(username = utente_ricorsione.username, id_utente = utente_ricorsione.id, utente = instance).exists()
				
				if (esistenza_nuovo_user_ricorsione is False) and (esistenza_in_white_ricorsione is False):
					
					check_limite(api)				
					mega_lista_utenti.append(utente_ricorsione.id)
					try:
						y = api.follow_user(user_id = utente_ricorsione.id)
					
						nuovo_user_blackilist2 = BlacklistUtenti(username = utente_ricorsione.username, id_utente = utente_ricorsione.id, utente = instance, unfollowato = False)
						nuovo_user_blackilist2.save()
					
						time.sleep(65)
					except:
						logger.error("how_i_met_your_follower", exc_info=True)
						pass
										
		cursore = get_cursore(follow_ricorsione)     
	
	for utente_id in mega_lista_utenti:
		try:
			api.unfollow_user(user_id = utente_id)
		
			utente_unfollowato = BlacklistUtenti.objects.get(id_utente = utente_id, utente = instance)
			utente_unfollowato.unfollowato = True
			utente_unfollowato.save()
		
			check_limite(api)
			time.sleep(65)
		except:
			logger.error("how_i_met_your_follower-unfollow", exc_info=True)
			pass
	
	avvia_task_pulizia_follower(access_token, instance)
		
	#Finito il ciclo chiudo il task
	ts = FollowTaskStatus.objects.get(completato = False, utente = instance)
	ts.completato = True
	ts.save()
						
	return 'Fine follower'

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
	
@shared_task   
def avvia_task_pulizia_follower(token, instance):	
	
	api = InstagramAPI(
		access_token = token,
		client_ips = MIOIP,
		client_secret = "e42bb095bdc6494aa351872ea17581ac"
	)
	
	utenti_da_unfolloware = BlacklistUtenti.objects.filter(utente = instance, unfollowato = False)
	for utente in utenti_da_unfolloware:
		user_id = utente.id_utente 
				
		check_limite(api)			
		try:
			api.unfollow_user(user_id = user_id)
			utente.unfollowato = True
			utente.save()			
			time.sleep(65)
		except:
			logger.error("avvia_task_pulizia_follower", exc_info=True)
			pass
			
	return "Fine pulizia"				
	


	
