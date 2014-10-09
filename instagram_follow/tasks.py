from __future__ import absolute_import

from celery import shared_task
from .models import BlacklistUtenti, WhitelistUtenti, UtentiRivali
from pagamenti.views import abbonamento_valido
from accesso.models import TaskStatus, Utente
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
		
		if task_diretto:
			task_obj = TaskStatus.objects.get(utente = instance, sorgente = "unfollow")
			task_completato = task_obj.completato

			abbonamento_is_valido = abbonamento_valido(instance)

			if abbonamento_is_valido is False:
				task_obj.delete()
				
				return "Stop unfollow per scadenza abbonamento"
			
			if task_completato:
				task_obj.delete()
				return "Stop unfollow"
				
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
		task.delete()
		
		return "Fine pulizia"
			
	return "Fine pulizia"				
			
			
@shared_task
def start_follow(instance, api):
	id_task = start_follow.request.id	
	nuovo_task = TaskStatus(task_id = id_task, completato = False, utente = instance, sorgente = "follow")
	nuovo_task.save()
	
	access_token = instance.tokens['access_token']
	
	tutti_rivali = UtentiRivali.objects.filter(utente = instance).order_by('numero_follower').values()
	
	contatore = 0
	
	for rivale in tutti_rivali:
		
		id_rivale = rivale['id_utente']
		
		cursore = None
		uscita = False
		
		while uscita is False:
			
			check_limite(api)
			followed_by_obj = api.user_followed_by(id_rivale, cursor = cursore)
			check_limite(api)
			
			utenti = followed_by_obj[0]
			
			for utente in utenti:

				abbonamento_is_valido = abbonamento_valido(instance)

				task_obj = TaskStatus.objects.get(utente = instance, sorgente = "follow")
				task_completato = task_obj.completato

				if abbonamento_is_valido is False:
					task_obj.delete()

					task_obj_accesso = TaskStatus.objects.get(utente = instance, sorgente = "accesso", completato = False)
					task_obj_accesso.delete()
					return "Stop follow per abbonamento scaduto"
				
				if task_completato:
					task_obj.delete()
					return "Fine follow"
				else:
					user_obj = Utente.objects.get(utente = instance)
					follow_totali = user_obj.follow_totali
					follow_sessione = user_obj.follow_sessione	
					
					try:
						esistenza_nuovo_user = BlacklistUtenti.objects.filter(id_utente = utente.id, utente = instance).exists()				
						esistenza_in_white = WhitelistUtenti.objects.filter(id_utente = utente.id, utente = instance).exists()			
			
						relationship = api.user_relationship(user_id = utente.id)
						is_private = relationship.target_user_is_private
						check_limite(api)
						
						if (esistenza_nuovo_user is False) and (esistenza_in_white is False) and (is_private is False):
					
							api.follow_user(user_id = utente.id)
							check_limite(api)
				
							nuovo_user_blackilist = BlacklistUtenti(username = utente.username, id_utente = utente.id, utente = instance, unfollowato = False)
							nuovo_user_blackilist.save()
					
							user_obj.follow_totali = follow_totali + 1
							user_obj.follow_sessione = follow_sessione + 1
							user_obj.save()
					
							contatore = contatore + 1
							contatore = check_contatore(contatore, access_token, instance)
							
							time.sleep(65)	
							
					except InstagramAPIError as errore:
						errore_mortale(errore, instance)						
					except:
						logger.error("how_i_met_your_follower", exc_info=True)
						pass
					
			cursore, uscita = get_cursore(followed_by_obj)
			
	task_da_eliminare = TaskStatus.objects.get(task_id = id_task, completato = False, utente = instance, sorgente = "follow")
	task_da_eliminare.delete()								
								
def check_contatore(contatore, token, instance):
	limite = 180
	
	if contatore > limite:
		avvia_task_pulizia_follower(token, instance, False)
		contatore = 0
		
	return contatore

