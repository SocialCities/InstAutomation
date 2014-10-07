from __future__ import absolute_import

from django.conf import settings
from celery import shared_task
from .models import ListaTag
from accesso.models import TaskStatus, Utente
from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI
from instagram import InstagramAPIError
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
		for singolo_tag in tutti_tag:
			task_obj = TaskStatus.objects.get(utente = user_instance, sorgente = "like")
			task_completato = task_obj.completato	
		
			if task_completato:
				task_obj.delete()
				non_finito = False
				break
				
			nome_tag = singolo_tag['keyword']
		
			try:				
				chiamata_like(api, nome_tag, user_instance)					
				
			except InstagramAPIError as errore:
				errore_mortale(errore, user_instance)	
												
			except:
				logger.error("insta_like", exc_info=True)
				pass
				
				
	return 'Fine Like'
		

def chiamata_like(api, nome_tag, user_instance):
	check_limite(api)
	
	tag_search = api.tag_recent_media(count = 10, tag_name = nome_tag)
	check_limite(api)
	
	for foto in tag_search[0]:	
		
		task_obj = TaskStatus.objects.get(utente = user_instance, sorgente = "like")
		task_completato = task_obj.completato	
		
		if task_completato:
			return "Like stoppato"						
		else:			
			user_obj = Utente.objects.get(utente = user_instance)
			like_messi = user_obj.like_totali
			like_sessione = user_obj.like_sessione
			
			id_elemento = foto.id
			conto_like = foto.like_count		
			link_foto = foto.link		
			
			if conto_like < 100:
				try:
					api.like_media(id_elemento)
					
					user_obj.like_totali = like_messi + 1
					user_obj.like_sessione = like_sessione + 1
					user_obj.save()				
					
					time.sleep(40)
				
				except InstagramAPIError as errore:
					if errore.error_type == "APINotAllowedError":
						pass
					else:
						logger.error("chiamata_like", exc_info=True)
						pass										 						
				except:
					logger.error("chiamata_like", exc_info=True)
					pass				
				
	
