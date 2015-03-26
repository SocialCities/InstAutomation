from __future__ import absolute_import

from celery import shared_task
from .models import BlacklistUtenti, WhitelistUtenti, UtentiRivali
from pagamenti.views import abbonamento_valido
from accesso.models import TaskStatus, Utente
from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError, InstagramClientError 
from django.db.models import F
from instautomation.utility import get_cursore, check_limite, errore_mortale
from django.db import transaction
from django.conf import settings
import random
import time
import logging
import httplib2
logger = logging.getLogger('django')

MIOIP = settings.IP_LOCALE
CLIENT_SECRET = settings.INSTAGRAM_CLIENT_SECRET

from accesso.models import ValDelay

def get_min_max():
	valori = ValDelay.objects.get(pk=1)
	minimo = valori.delay_min
	massimo = valori.delay_max
	return minimo, massimo
	
@shared_task   
def avvia_task_pulizia_follower(token, instance, task_diretto, id_task_padre):
	
	api = InstagramAPI(
		access_token = token,
		client_ips = MIOIP,
		client_secret = CLIENT_SECRET 
	)

	#Funzione utile a pulire gli utenti rimasti appesi
	pulizia_utenti_mancanti(api, instance)

	utenti_da_unfolloware = BlacklistUtenti.objects.filter(utente = instance, unfollowato = False).order_by('time_stamp')

	for utente in utenti_da_unfolloware.iterator():

		if task_diretto:
			id_task = avvia_task_pulizia_follower.request.id	
			task_obj = TaskStatus.objects.get(utente = instance, task_id = id_task)
		else:
			task_obj = TaskStatus.objects.get(utente = instance, task_id = id_task_padre)

		task_completato = task_obj.completato
		abbonamento_is_valido = abbonamento_valido(instance)

		if task_completato or (abbonamento_is_valido is False):
			#Riscrittura utile nel caso di abbonamento non valido
			task_obj.completato = True
			task_obj.save()

			return "Stop unfollow"

		user_id = utente.id_utente 
		check_limite(api)

		minimo, massimo = get_min_max()
		sleeping_time = random.randint(minimo, massimo)
		time.sleep(sleeping_time)	

		try:
			with transaction.commit_on_success():	
				api.unfollow_user(user_id = user_id)
				utente.unfollowato = True
				utente.save()

		except InstagramAPIError as errore:
			errore_mortale(errore, instance)

		except InstagramClientError as errore2:
			errore_mortale(errore2, instance)

		except httplib2.ServerNotFoundError:
			minimo, massimo = get_min_max()
			sleeping_time = random.randint(minimo, massimo)
			time.sleep(sleeping_time)	

	if task_diretto:
		id_task = avvia_task_pulizia_follower.request.id
		task_obj = TaskStatus.objects.get(utente = instance, task_id = id_task)
		task_obj.completato = True
		task_obj.save()

	return "Fine unfollow"
			
@shared_task
def start_follow(instance, api):

	access_token = instance.tokens['access_token']

	id_task = start_follow.request.id
	nuovo_task = TaskStatus(task_id = id_task, completato = False, utente = instance, sorgente = "follow")
	nuovo_task.save()

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

			for utente in iter(utenti):
				task_obj = TaskStatus.objects.get(task_id = id_task)
				task_completato = task_obj.completato

				abbonamento_is_valido = abbonamento_valido(instance)

				if task_completato or (abbonamento_is_valido is False):
					#Riscrittura utile nel caso di abbonamento non valido
					task_obj.completato = True
					task_obj.save()

					return "Stop Follow"

				else:
					try:
						with transaction.commit_on_success():
							esistenza_nuovo_user = BlacklistUtenti.objects.filter(id_utente = utente.id, utente = instance).exists()				
							esistenza_in_white = WhitelistUtenti.objects.filter(id_utente = utente.id, utente = instance).exists()			
				
							relationship = api.user_relationship(user_id = utente.id)
							is_private = relationship.target_user_is_private
							check_limite(api)
							
							if (esistenza_nuovo_user is False) and (esistenza_in_white is False) and (is_private is False):
								
								minimo, massimo = get_min_max()
								sleeping_time = random.randint(minimo, massimo)
								time.sleep(sleeping_time)	
								
								api.follow_user(user_id = utente.id)
								check_limite(api)
					
								nuovo_user_blackilist = BlacklistUtenti(username = utente.username, id_utente = utente.id, utente = instance, unfollowato = False)
								nuovo_user_blackilist.save()

								Utente.objects.filter(utente = instance).update(follow_totali = F('follow_totali') + 1)
								Utente.objects.filter(utente = instance).update(follow_sessione = F('follow_sessione') + 1)
						
								contatore = contatore + 1
								contatore = check_contatore(contatore, access_token, instance, id_task)		
														
					except InstagramAPIError as errore:
						errore_mortale(errore, instance)

					except InstagramClientError as errore2:
						errore_mortale(errore2, instance)

					except httplib2.ServerNotFoundError:
						minimo, massimo = get_min_max()
   						sleeping_time = random.randint(minimo, massimo)
   						time.sleep(sleeping_time)	
					
			cursore, uscita = get_cursore(followed_by_obj)
	
	avvia_task_pulizia_follower(access_token, instance, False, id_task)	

	task_da_chiudure = TaskStatus.objects.get(task_id = id_task)
	task_da_chiudure.completato = True
	task_da_chiudure.save()			
		
								
def check_contatore(contatore, token, instance, id_task_padre):
	limite = 2
	
	if contatore > limite:
		avvia_task_pulizia_follower(token, instance, False, id_task_padre)
		contatore = 0
		
	return contatore


def pulizia_utenti_mancanti(api, instance):

	all_utenti = BlacklistUtenti.objects.filter(utente = instance, unfollowato = False)

	cursore = None
	uscita = False
	persone_che_seguo = []
	while uscita is False:
		followed_by_obj = api.user_follows(cursor = cursore)
		utenti = followed_by_obj[0]
		
		for utente in utenti:
			persone_che_seguo.append(utente.username)
		
		cursore, uscita = get_cursore(followed_by_obj)

	for utente in all_utenti.iterator():
	 	username = utente.username
		
		if username not in persone_che_seguo:
			utente.delete()