from __future__ import absolute_import

from django.conf import settings
from celery import shared_task
from .models import ListaTag
from accesso.models import TaskStatus, Utente
from pagamenti.views import abbonamento_valido
from instagram.bind import InstagramAPIError, InstagramClientError 
from django.db.models import F

import time
import logging
logger = logging.getLogger('django')

from instautomation.utility import check_limite, errore_mortale

MIOIP = settings.IP_LOCALE
CLIENT_SECRET = settings.INSTAGRAM_CLIENT_SECRET
   
@shared_task
def like_task(access_token, user_instance, api):
	id_nuovo_task = like_task.request.id
	nuovo_task = TaskStatus(task_id = id_nuovo_task, completato = False, utente = user_instance, sorgente = "like")
	nuovo_task.save()

	tutti_tag = ListaTag.objects.filter(utente = user_instance).values()

	while True: 
		for singolo_tag in iter(tutti_tag):

			check_task = TaskStatus.objects.get(task_id = id_nuovo_task)
			task_completato = check_task.completato
			abbonamento_is_valido = abbonamento_valido(user_instance)

			if task_completato or (abbonamento_is_valido is False):
				check_task.completato = True
				check_task.save()

				return "Fine Like"

			nome_tag = singolo_tag['keyword']

			check_limite(api)
			tag_search = api.tag_recent_media(count = 10, tag_name = nome_tag)
			check_limite(api)

			for foto in iter(tag_search[0]):

				check_task = TaskStatus.objects.get(task_id = id_nuovo_task)
				task_completato = check_task.completato
				abbonamento_is_valido = abbonamento_valido(user_instance)

				if task_completato or (abbonamento_is_valido is False):
					#Riscrittura utile nel caso di abbonamento non valido
					check_task.completato = True
					check_task.save()

					return "Fine Like"

				id_elemento = foto.id
				conto_like = foto.like_count

				if conto_like < 100:
					try:
						time.sleep(90)
						api.like_media(id_elemento)

						Utente.objects.filter(utente = user_instance).update(like_totali = F('like_totali') + 1)
						Utente.objects.filter(utente = user_instance).update(like_sessione = F('like_sessione') + 1)								
					
					except InstagramAPIError as errore:
						errore_mortale(errore, user_instance)

					except InstagramClientError as errore2:
						errore_mortale(errore2, user_instance)	
	
	return "Stop like"						