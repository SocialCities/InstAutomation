from __future__ import absolute_import

from celery import shared_task
from .models import ListaTag, BlacklistFoto, LikeTaskStatus
from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI
import time
import logging
logger = logging.getLogger('django')


MIOIP = '95.238.61.84'
    
@shared_task   
def insta_task(access_token, user_instance):
	
	api = InstagramAPI(
        access_token=access_token,
        client_ips = MIOIP,
        client_secret="e42bb095bdc6494aa351872ea17581ac"
    )
    
	check_limite(api)
	
	tutti_tag = ListaTag.objects.filter(utente = user_instance)
	
	#while True: 
	for singolo_tag in tutti_tag:
		nome_tag = singolo_tag.keyword
	
		try:
			chiamata_like(api, nome_tag, user_instance)

		except:
			pass
			logger.error("insta_like", exc_info=True)
	#fine while						
	return 'Fine Like'
		
def chiamata_like(api, nome_tag, user_instance):
	
	tag_search = api.tag_recent_media(count = 10, tag_name = nome_tag)
	
	check_limite(api)

	for foto in tag_search[0]:		
		id_elemento = foto.id
		conto_like = foto.like_count		
		link_foto = foto.link
		
		check_foto_liked = BlacklistFoto.objects.filter(id_foto = id_elemento, utente = user_instance).exists()
			
		if check_foto_liked is False:				
			if conto_like < 100:
				try:	
					api.like_media(id_elemento)
					
					check_limite(api)
					
					comm = BlacklistFoto(id_foto = id_elemento, link_foto = link_foto, utente = user_instance)
					comm.save()
						
					time.sleep(40)						
				except:
					logger.error("chiamata_like", exc_info=True)
					pass
					
def check_limite(api):
	x_ratelimit_remaining = api.x_ratelimit_remaining
	if (x_ratelimit_remaining < 10) and (x_ratelimit_remaining is not None):
		time.sleep(3600)
