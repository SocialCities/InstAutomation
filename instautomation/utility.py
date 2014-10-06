from __future__ import absolute_import

from accesso.models import TaskStatus, Utente
from instagram.client import InstagramAPI

from celery.task.control import revoke, broadcast

from django.core.mail import send_mail, EmailMultiAlternatives 

import urlparse
import time

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
		task_obj = TaskStatus.objects.get(completato = False, utente = instance, sorgente = "follow")
		task_obj.completato	= True
		task_obj.save()	
	
	#Unfollow
	task_attivi_esistenza_unfollow = TaskStatus.objects.filter(completato = False, utente = instance, sorgente = "unfollow").exists()
	
	if task_attivi_esistenza_unfollow:
		task_obj = TaskStatus.objects.get(completato = False, utente = instance, sorgente = "unfollow")
		task_obj.completato	= True
		task_obj.save()
		
	#Like			
	task_attivi_esistenza_like = TaskStatus.objects.filter(completato = False, utente = instance, sorgente = "like").exists()
	
	if task_attivi_esistenza_like:
		task_obj = TaskStatus.objects.get(completato = False, utente = instance, sorgente = "like")
		task_obj.completato	= True
		task_obj.save()		
		
	#Accesso	
	task_attivi_esistenza_accesso = TaskStatus.objects.filter(completato = False, utente = instance, sorgente = "accesso").exists()
	
	if task_attivi_esistenza_accesso:
		task_obj = TaskStatus.objects.get(completato = False, utente = instance, sorgente = "accesso")
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
		pass
				
def avviso_email(email_utente):
    subject, from_email, to = '[Instautomation] Errore nel sistema', 'admindjango@instautomation.com', email_utente
	
    text_content = "Ciao! Scoppia tutto!"
    html_content = "Ciao! <br/>Scoppia tutto!"
	
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    			 	
