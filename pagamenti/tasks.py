from celery import shared_task
from django.core.mail import EmailMultiAlternatives 
from datetime import date
from .models import Pacchetti
from accesso.models import Utente

@shared_task
def cron_scadenza_pacchetto():
	oggi = date.today() 
	all_pack = Pacchetti.objects.filter(data_scadenza = oggi).values('utente')
	for pack in all_pack:
		id_utente = pack['utente']
		email_utente = Utente.objects.get(pk = id_utente).email

		from_email = 'info@instautomation.com'
		to = email_utente
		subject = "Instautomation - Your package has expired"
		text_content = "Hi!<br/><br/>Your Instautomation package has expired.<br/> To continue with your subscription, just sign up again on the subscription page.<br/><br/>Go to instautomation.com now!<br/><br/>If you have any questions about your subscription, please contact info@instautomation.com"
		html_content = text_content
		
		msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
		msg.attach_alternative(html_content, "text/html")
		msg.send()