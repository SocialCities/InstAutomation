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
		
	return 'Started!'

@shared_task 
def elimina_vecchi_utenti():
    now = datetime.now()
    
    tre_giorni_fa = now - timedelta(3)
	
    utenti_da_eliminare = BlacklistUtenti.objects.filter(unfollowato = True, time_stamp__lt = tre_giorni_fa)
    utenti_da_eliminare.delete()
    print 42

    
@shared_task 
def pulsantone_rosso(oggetto, no_html, con_html):

	all_tasks = TaskStatus.objects.all().iterator()
	all_utenti = Utente.objects.all().iterator()

	now = datetime.now()

	for task_obj in all_tasks:
		task_obj.completato	= True
		task_obj.save()

	for utente in all_utenti:
		utente.data_blocco_forzato = now
		utente.save()
		email_pulsantone.delay(utente.email, oggetto, no_html, con_html)

	print "Don't Panic!"

@shared_task
def email_pulsantone(email_utente, oggetto, no_html, con_html):
    subject, from_email, to = oggetto, 'info@instautomation.com', email_utente

    text_content = no_html
    html_content = con_html
	
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()	

@shared_task
def invio_email_primo_avvio(email, username):
    subject, from_email, to = '[Instautomation] Welcome!', 'info@instautomation.com', email
	
    html_content = "Dear "+username+",<br/> \
					welcome to Instautomation!<br/>\
					Actually, we're on Beta-version mode and the system is opened to few users;<br/>\
					congrats for being one of the chosen.<br/>\
					You can start to optimize your Insta profile by trying the '2days4free' package.<br/>\
					Anyway, we strongly recommend you to read our Term of Service before starting to use Instautomation.<br/>\
					Feel free to share any suggestion or problem at info@instautomation.com.<br/>\
					Kind regards,<br/>\
					Instautomation Team"

    text_content = html_content			
	
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()		