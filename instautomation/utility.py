from __future__ import absolute_import

from accesso.models import TaskStatus, Utente

from django.core.mail import EmailMultiAlternatives 

import urlparse
import time
import logging
logger = logging.getLogger('django')

def get_cursore(object_to_check):
	cursore = prendi_valore_indice('cursor', object_to_check)
	
	if cursore is None:
		return cursore, True
	else:
		return cursore, False
			
def get_max_id(object_to_check):
	return prendi_valore_indice('max_id', object_to_check)	

def prendi_valore_indice(stringa, object_to_check):
	blocco_pagination = object_to_check[1]
	
	if blocco_pagination is None:
		return None
	else:
		o = urlparse.urlparse(blocco_pagination)
		query = o.query
		query_parsed = urlparse.parse_qs(query)
		cursore = query_parsed[stringa][0]
		return cursore	

def check_limite(api):
	x_ratelimit_remaining = api.x_ratelimit_remaining
	if (x_ratelimit_remaining < 10) and (x_ratelimit_remaining is not None):
		time.sleep(3600)	
		
def kill_all_tasks(instance):
	
	#Follow
	task_attivi_esistenza_follow = TaskStatus.objects.filter(completato = False, utente = instance, sorgente = "follow").exists()	
	
	if task_attivi_esistenza_follow:
		all_task_obj = TaskStatus.objects.filter(completato = False, utente = instance, sorgente = "follow")
		for task_obj in all_task_obj:
			task_obj.completato	= True
			task_obj.save()	
	
	#Unfollow
	task_attivi_esistenza_unfollow = TaskStatus.objects.filter(completato = False, utente = instance, sorgente = "unfollow").exists()
	
	if task_attivi_esistenza_unfollow:
		all_task_obj = TaskStatus.objects.filter(completato = False, utente = instance, sorgente = "unfollow")
		for task_obj in all_task_obj:
			task_obj.completato	= True
			task_obj.save()
		
	#Like			
	task_attivi_esistenza_like = TaskStatus.objects.filter(completato = False, utente = instance, sorgente = "like").exists()
	
	if task_attivi_esistenza_like:
		all_task_obj = TaskStatus.objects.filter(completato = False, utente = instance, sorgente = "like")
		for task_obj in all_task_obj:
			task_obj.completato	= True
			task_obj.save()		
		
	#Accesso	
	task_attivi_esistenza_accesso = TaskStatus.objects.filter(completato = False, utente = instance, sorgente = "accesso").exists()
	
	if task_attivi_esistenza_accesso:
		all_task_obj = TaskStatus.objects.filter(completato = False, utente = instance, sorgente = "accesso")
		for task_obj in all_task_obj:
			task_obj.completato	= True
			task_obj.save()		

						
def errore_mortale(errore, instance):
	if errore.error_type == "OAuthAccessTokenException":
		
		utente_obj = Utente.objects.get(utente = instance)
		email_utente = utente_obj.email
		utente_obj.token_block = True
		utente_obj.save()
		
		avviso_email(email_utente)	
		
		kill_all_tasks(instance)	
	else:
		logger.error("errore mortale", exc_info=True)
		pass
				
def avviso_email(email_utente):
    subject, from_email, to = '[Instautomation] Errore nel sistema', 'admindjango@instautomation.com', email_utente
	
    text_content = "Ciao! Scoppia tutto!"
    html_content = "Ciao! <br/>Scoppia tutto!"
	
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    			 	
