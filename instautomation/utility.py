from __future__ import absolute_import

from accesso.models import TaskStatus, Utente
from instagram.client import InstagramAPI

from celery.task.control import revoke

from django.core.mail import send_mail, EmailMultiAlternatives 

import urlparse
import time

def get_cursore(object_to_check):
	return prendi_valore_indice('cursor', object_to_check)	

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
	task_attivi_esistenza = TaskStatus.objects.filter(completato = False, utente = instance).exists()
	
	if task_attivi_esistenza:
		task_attivi = TaskStatus.objects.filter(completato = False, utente = instance)
		for task_attivo in task_attivi:
			task_id = task_attivo.task_id
			task_attivo.completato = True
			task_attivo.save()
			revoke(task_id, terminate=True, signal="KILL")		
						
def errore_mortale(errore, instance):
	if errore.error_type == "OAuthAccessTokenException":
		
		utente_obj = Utente.objects.get(utente = instance)
		email_utente = utente_obj.email
		utente_obj.token_block = True
		utente_obj.save()
		
		avviso_email(email_utente)	
		
		kill_all_tasks(instance)	
	else:
		pass
				
def avviso_email(email_utente):
    subject, from_email, to = '[Instautomation] Errore nel sistema', 'admindjango@instautomation.com', email_utente
	
    text_content = "Ciao! Scoppia tutto!"
    html_content = "Ciao! <br/>Scoppia tutto!"
	
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    			 	
