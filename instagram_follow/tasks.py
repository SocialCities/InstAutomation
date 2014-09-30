from __future__ import absolute_import

from celery import shared_task
from .models import BlacklistUtenti, WhitelistUtenti, UtentiRivali
from accesso.models import TaskStatus
from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI
from instagram import InstagramAPIError

from instautomation.utility import get_cursore, check_limite, errore_mortale

from django.conf import settings
import time
import logging
logger = logging.getLogger('django')

MIOIP = settings.IP_LOCALE
CLIENT_SECRET = settings.INSTAGRAM_CLIENT_SECRET
	
@shared_task   
def avvia_task_pulizia_follower(token, instance, task_diretto):	
	
	api = InstagramAPI(
		access_token = token,
		client_ips = MIOIP,
		client_secret = CLIENT_SECRET 
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
			
		except InstagramAPIError as errore:
			errore_mortale(errore, instance)
											
		except:
			logger.error("avvia_task_pulizia_follower", exc_info=True)
			pass
			
	if task_diretto:		
	
		task = TaskStatus.objects.get(completato = False, utente = instance)	
		task.completato = True
		task.save()	
			
	return "Fine pulizia"				
			
	
@shared_task  
def start_follow(instance, api):
	access_token = instance.tokens['access_token']
    
	all_rivali = UtentiRivali.objects.filter(utente = instance).values()
    
	contatore = 0
    
	for rivale in all_rivali:
		id_rivale = rivale['id_utente']
		
		contatore = how_i_met_your_follower(api, access_token, instance, id_rivale, contatore)
  
def how_i_met_your_follower(api, access_token, instance, id_rivale, contatore):

    check_limite(api)
    try:
		followed_by_obj = api.user_followed_by(id_rivale)	
		
    except InstagramAPIError as errore:
		errore_mortale(errore, instance)	
	
    check_limite(api)
    
    utenti = followed_by_obj[0]
    for utente in utenti:
			try:
				
				#Collo
				esistenza_nuovo_user = BlacklistUtenti.objects.filter(id_utente = utente.id, utente = instance).exists()				
				esistenza_in_white = WhitelistUtenti.objects.filter(id_utente = utente.id, utente = instance).exists()
			
				relationship = api.user_relationship(user_id = utente.id)
				is_private = relationship.target_user_is_private
				check_limite(api)		
			
				if (esistenza_nuovo_user is False) and (esistenza_in_white is False) and (is_private is False):
					
					#x = api.follow_user(user_id = utente.id)
					check_limite(api)
				
					nuovo_user_blackilist = BlacklistUtenti(username = utente.username, id_utente = utente.id, utente = instance, unfollowato = False)
					nuovo_user_blackilist.save()
					
					contatore = contatore + 1
					contatore = check_contatore(contatore, access_token, instance)
				
					time.sleep(65)
					
			except InstagramAPIError as errore:
				errore_mortale(errore, instance)	
					
			except:
				logger.error("how_i_met_your_follower", exc_info=True)
				pass

		
    cursore = get_cursore(followed_by_obj)
	
    while cursore is not None:		
		follow_ricorsione = api.user_followed_by(id_rivale, cursor = cursore)
		
		check_limite(api)
		
		utenti_ricorsione = follow_ricorsione[0]
		for utente_ricorsione in utenti_ricorsione:
			try:
				
				#Collo di bottiglia
				esistenza_nuovo_user_ricorsione = BlacklistUtenti.objects.filter(id_utente = utente_ricorsione.id, utente = instance).exists()
				esistenza_in_white_ricorsione = WhitelistUtenti.objects.filter(id_utente = utente_ricorsione.id, utente = instance).exists()
				
				relationship = api.user_relationship(user_id = utente_ricorsione.id)
				is_private = relationship.target_user_is_private
				check_limite(api)	
				
				if (esistenza_nuovo_user_ricorsione is False) and (esistenza_in_white_ricorsione is False) and (is_private is False):
					
					#y = api.follow_user(user_id = utente_ricorsione.id)
					check_limite(api)
					
					nuovo_user_blackilist2 = BlacklistUtenti(username = utente_ricorsione.username, id_utente = utente_ricorsione.id, utente = instance, unfollowato = False)
					nuovo_user_blackilist2.save()
					
					contatore = contatore +1
					contatore = check_contatore(contatore, access_token, instance)
					
					time.sleep(65)
					
			except InstagramAPIError as errore:
				errore_mortale(errore, instance)
						
			except:
				logger.error("how_i_met_your_follower", exc_info=True)
				pass
										
		cursore = get_cursore(follow_ricorsione)     
						
    return contatore 


def check_contatore(contatore, token, instance):
	limite = 180
	
	if contatore > limite:
		avvia_task_pulizia_follower(token, instance, False)
		contatore = 0
	
	return contatore
