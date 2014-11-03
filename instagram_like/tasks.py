from __future__ import absolute_import

from django.conf import settings
from celery import shared_task
from .models import ListaTag
from accesso.models import TaskStatus, Utente
from pagamenti.views import abbonamento_valido
from instagram.bind import InstagramAPIError
from celery.exceptions import Terminated

import time
import logging
logger = logging.getLogger('django')

from instautomation.utility import check_limite, errore_mortale

MIOIP = settings.IP_LOCALE
CLIENT_SECRET = settings.INSTAGRAM_CLIENT_SECRET
   
    
@shared_task(throws=Terminated)   
def like_task(access_token, user_instance, api):	
	
	id_task1 = like_task.request.id
	nuovo_task1 = TaskStatus(task_id = id_task1, completato = False, utente = user_instance, sorgente = "like")
	nuovo_task1.save()	
	
	tutti_tag = ListaTag.objects.filter(utente = user_instance).values()
	
	non_finito = True
	
	while non_finito: 
		if len(tutti_tag) == 0:
			non_finito = False
			
		for singolo_tag in iter(tutti_tag):
			controllo_esistenza_task_obj = TaskStatus.objects.filter(utente = user_instance, sorgente = "like", task_id = id_task1).exists()
			if controllo_esistenza_task_obj is False:
				continue
			task_obj = TaskStatus.objects.get(utente = user_instance, sorgente = "like", task_id = id_task1)			
			task_completato = task_obj.completato	

			abbonamento_is_valido = abbonamento_valido(user_instance)

			if abbonamento_is_valido is False:
				task_obj.delete()

				task_obj_accesso = TaskStatus.objects.get(utente = user_instance, sorgente = "accesso", completato = False)
				task_obj_accesso.delete()
				non_finito = False
				break
		
			if task_completato:
				task_obj.delete()
				non_finito = False
				break
				
			nome_tag = singolo_tag['keyword']
		
			try:				
				non_finito = chiamata_like(api, nome_tag, user_instance, id_task1)					
				
			except InstagramAPIError as errore:
				errore_mortale(errore, user_instance)												
													
	return 'Fine Like'
		

def chiamata_like(api, nome_tag, user_instance, id_task):
	check_limite(api)
	
	tag_search = api.tag_recent_media(count = 10, tag_name = nome_tag)
	check_limite(api)
	
	for foto in iter(tag_search[0]):	
		
		task_obj = TaskStatus.objects.get(utente = user_instance, sorgente = "like", task_id = id_task)
		task_completato = task_obj.completato	

		abbonamento_is_valido = abbonamento_valido(user_instance)

		if abbonamento_is_valido is False:
			task_obj.delete()	

			task_obj_accesso = TaskStatus.objects.get(utente = user_instance, sorgente = "accesso", completato = False)
			task_obj_accesso.delete()		
			return False	
		
		if task_completato:
			task_obj.delete()
			return False					
		else:			
			user_obj = Utente.objects.get(utente = user_instance)
			like_messi = user_obj.like_totali
			like_sessione = user_obj.like_sessione
			
			id_elemento = foto.id
			conto_like = foto.like_count	
			
			if conto_like < 100:
				try:
					time.sleep(60)
					#print id_elemento
					#print foto.link
					api.like_media(id_elemento)
					
					user_obj.like_totali = like_messi + 1
					user_obj.like_sessione = like_sessione + 1
					user_obj.save()								
				
				except InstagramAPIError as errore:
					errore_mortale(errore, user_instance)	
													
	return True	