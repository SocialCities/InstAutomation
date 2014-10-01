from __future__ import absolute_import

from django.conf import settings
from celery import shared_task
from .models import ListaTag, BlacklistFoto
from accesso.models import TaskStatus
from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI
from instagram import InstagramAPIError

import time
import logging
logger = logging.getLogger('django')

from instautomation.utility import check_limite, errore_mortale

MIOIP = settings.IP_LOCALE
CLIENT_SECRET = settings.INSTAGRAM_CLIENT_SECRET
    
@shared_task   
def insta_task(access_token, user_instance, api):	
	
	tutti_tag = ListaTag.objects.filter(utente = user_instance).values()
	
	while True: 
		for singolo_tag in tutti_tag:
			nome_tag = singolo_tag['keyword']
		
			try:
				chiamata_like(api, nome_tag, user_instance)
				
			except InstagramAPIError as errore:
				errore_mortale(errore, user_instance)	
				
			except:
				logger.error("insta_like", exc_info=True)
				pass
				
	#fine while	
				
	return 'Fine Like'
		

def chiamata_like(api, nome_tag, user_instance):
	check_limite(api)
	
	tag_search = api.tag_recent_media(count = 10, tag_name = nome_tag)
	
	check_limite(api)
	
	for foto in tag_search[0]:		
		id_elemento = foto.id
		conto_like = foto.like_count		
		link_foto = foto.link		
		
		if conto_like < 100:
			try:
				api.like_media(id_elemento)
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
				
				
						
#def chiamata_like_tmp(api, nome_tag, user_instance):
#	
#	check_limite(api)
#	
#	tag_search = api.tag_recent_media(count = 10, tag_name = nome_tag)
#	
#	check_limite(api)
#	
#	for foto in tag_search[0]:		
#		id_elemento = foto.id
#		conto_like = foto.like_count		
#		link_foto = foto.link		
		
		#Possibile collo di bottiglia
#		check_foto_liked = BlacklistFoto.objects.filter(id_foto = id_elemento, utente = user_instance).exists()	
			
#		if check_foto_liked is False:				
#			if conto_like < 100:
#				try:	
					
#					#api.like_media(id_elemento)					
#					check_limite(api)
#					
#					comm = BlacklistFoto(id_foto = id_elemento, link_foto = link_foto, utente = user_instance)
#					comm.save()
						
#					time.sleep(40)
					
#				except InstagramAPIError as errore:
#					if errore.error_type == "APINotAllowedError":
#						pass
#					else:
#						logger.error("chiamata_like", exc_info=True)
#						pass						 						
#				except:
#					logger.error("chiamata_like", exc_info=True)
#					pass
					
