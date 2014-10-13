from __future__ import absolute_import

from django.conf import settings
from django.core.mail import EmailMultiAlternatives 
from celery import shared_task

from instagram.client import InstagramAPI

from datetime import datetime, timedelta
import logging
logger = logging.getLogger('django')

MIOIP = settings.IP_LOCALE
CLIENT_SECRET = settings.INSTAGRAM_CLIENT_SECRET

from instagram_like.tasks import like_task
from instagram_follow.tasks import start_follow
from instagram_follow.views import update_whitelist
from instagram_follow.models import BlacklistUtenti

from .models import TaskStatus, Utente

@shared_task   
def start_task(token, instance):
	
	api = InstagramAPI(
		access_token = token,
		client_ips = MIOIP,
		client_secret = CLIENT_SECRET
	)	
	
	update_whitelist(api, instance)
	
	like_task.delay(token, instance, api)	
	start_follow.delay(instance, api)
		
	return 'yo'

@shared_task 
def elimina_vecchi_utenti():
    now = datetime.now()
    
    tre_giorni_fa = now - timedelta(3)
	
    utenti_da_eliminare = BlacklistUtenti.objects.filter(unfollowato = True, time_stamp__lt = tre_giorni_fa)
    utenti_da_eliminare.delete()
    print 42

    
@shared_task 
def pulsantone_rosso():

	all_tasks = TaskStatus.objects.all().iterator()
	all_utenti = Utente.objects.all().iterator()

	now = datetime.now()

	for task_obj in all_tasks:
		task_obj.completato	= True
		task_obj.save()

	for utente in all_utenti:
		utente.data_blocco_forzato = now
		utente.save()
		email_pulsantone.delay(utente.email)

	print "Don't Panic!"

@shared_task
def email_pulsantone(email_utente):
    subject, from_email, to = '[Instautomation] Pausa pausa', 'admindjango@instautomation.com', email_utente
	
    text_content = "Ciao! Faccio la cacca di sera di mattina di notte"
    html_content = "Ciao! <br/>Faccio la cacca di sera di mattina di notte!"
	
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()	