from __future__ import absolute_import

from accesso.models import trackStats
from InstaTrezzi.utility import get_cursore, check_limite, get_max_id

from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives

from celery import shared_task
from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

import time
import logging
logger = logging.getLogger('django')

from InstaTrezzi.utility import check_limite

MIOIP = settings.IP_LOCALE
    
@shared_task   
def report_task(instance):		
	access_token = instance.tokens['access_token']
	
	api = InstagramAPI(
			access_token = access_token,
			client_ips = MIOIP,
			client_secret = "e42bb095bdc6494aa351872ea17581ac"
	)	
	
	stats_obj = trackStats.objects.get(utente = instance)	
	follower_iniziali = stats_obj.follower_iniziali
	follower_iniziali = float(follower_iniziali)
	
	informazioni = api.user()
	follower_attuali = informazioni.counts['followed_by']
	follower_attuali = float(follower_attuali)
	
	#Variazione percentuali numero di follower
	percentuale = ( (follower_attuali - follower_iniziali) / follower_attuali ) * 100
	percentuale = round(percentuale, 2)
	
	#I tag che ho usano maggiormente
	lista_ordinata, lista_tag = statistiche_tag(api)
	
	primo = lista_ordinata[0]
	tag_primo = lista_tag[primo]
	
	secondo = lista_ordinata[1]
	tag_secondo = lista_tag[secondo]
	
	terzo = lista_ordinata[2]
	tag_terzo = lista_tag[terzo]
	
	#Miei follower con piu' follower
	lista_ordinata = follower_per_num_follower(api)
	
	primo_follower = lista_ordinata[0].username
	primo_follower_num_follower = lista_ordinata[0].num_follower
	 
	secondo_follower = lista_ordinata[1].username
	secondo_follower_num_follower = lista_ordinata[1].num_follower
	
	terzo_follower = lista_ordinata[2].username
	terzo_follower_num_follower = lista_ordinata[2].num_follower	
		
	return primo_follower + " - " + str(primo_follower_num_follower)
					


def follower_per_num_follower(api):
        
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
				
				utente_ricorsione.num_follower = numero_follower
				simply_user_obj_list.append(utente_ricorsione)				
			except:
				pass
		
		cursore = get_cursore(follow_ricorsione)		   	
	

    lista_ordinata = sorted(simply_user_obj_list, key = lambda user_obj: user_obj.num_follower, reverse=True)
    
    return lista_ordinata

def statistiche_tag(api):
	
	listone = []
	lista_tag = {}   

	prima_lista = api.user_recent_media()
	primo_elenco = prima_lista[0]
	
	for media in primo_elenco:
		if hasattr(media,'tags'):
			for tag in media.tags:
				nome_tag = tag.name
				if nome_tag in lista_tag:
					lista_tag[nome_tag] = lista_tag[nome_tag] + 1
				else:
					lista_tag[nome_tag] =  1
	
	cursore_pagina = get_max_id(prima_lista)
	
	while cursore_pagina is not None:
		lista_ricorsiva = api.user_recent_media(max_id = cursore_pagina)
		obj_lista_ricorsiva = lista_ricorsiva[0]
		
		for media in obj_lista_ricorsiva:
			if hasattr(media,'tags'):
				for tag in media.tags:
					nome_tag = tag.name
					if nome_tag in lista_tag:
						lista_tag[nome_tag] = lista_tag[nome_tag] + 1
					else:
						lista_tag[nome_tag] =  1
		
		cursore_pagina = get_max_id(lista_ricorsiva)
	
	
	lista_ordinata = sorted(lista_tag, key=lista_tag.get, reverse=True)	
		
	return lista_ordinata, lista_tag
	
