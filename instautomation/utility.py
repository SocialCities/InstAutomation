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

def errore_mortale(e, instance):
	username = instance.extra_data['username']
	if (e.status_code == 400):
		if (e.error_type == 'OAuthParameterException'):
			print username + " - " + e.error_message #Token errore
			utente_obj = Utente.objects.get(utente = instance)
			email_utente = utente_obj.email

			if utente_obj.token_block is False:

				utente_obj.token_block = True
				utente_obj.save()
				
				avviso_email(email_utente)	
				
				kill_all_tasks(instance)	
					
		elif (e.error_type == 'APINotAllowedError'):
			print username + " - " +  e.error_message
			time.sleep(180)

		elif (e.error_type == 'APINotFoundError'):
			print username + " - " +  e.error_message
			time.sleep(180)	
			
	elif (e.status_code == 429):
		print username + " - " +  e.error_message #Rate limited
		time.sleep(180)

	elif (e.status_code == 404):
		print username + " - " +  e.error_message #Rate limited
		time.sleep(180)	
		
	elif (e.status_code == 500):
		print username + " - " +  e.error_message #errore JSON
		time.sleep(180)
							
	elif (e.status_code == 502):
		print username + " - " +  e.error_message #errore JSON
		time.sleep(180)

	elif (e.status_code == 503):
		print username + " - " +  e.error_message #Rate limited	
		time.sleep(180)			
		
	elif (e.status_code == 504):
		print username + " - " +  e.error_message #errore JSON
		time.sleep(180)	
	else:
		time.sleep(180)		
		print username + " - " + 'errore mortale'
		print e.status_code
		logger.error("errore mortale", exc_info=True)	

				
def avviso_email(email_utente):
    subject, from_email, to = '[Instautomation] Access token issue', 'info@instautomation.com', email_utente
	
    text_content = "Dear user, your access token has been reset by Instagram. Log in Instagram and insert the chapta, then log in Instautomation and you'll be able to continue to use out system."
    html_content = "Dear user, your access token has been reset by Instagram.<br/>\
          Log in Instagram and insert the chapta, then log in Instautomation and you'll be able to continue to use out system."
	
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    			 	
