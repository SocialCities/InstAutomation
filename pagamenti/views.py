from __future__ import absolute_import

from .models import Pacchetti
from accesso.models import  Utente
from datetime import datetime, timedelta, date
from django.core.mail import EmailMultiAlternatives 
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from celery import shared_task

from social_auth.models import UserSocialAuth

import stripe

stripe.api_key = "sk_test_N9dMUTCNi6WM8O7mm2GiqFWT"
public_key_stripe = "pk_test_m4WooyEo8H5ACDmQJfMesph0"

def nuovo_pacchetto(instance, giorni):
	now = datetime.now()
	pacchetto_obj = Pacchetti(utente = instance, data_acquisto = now, giorni = giorni, attivato = False)
	pacchetto_obj.save()

def attiva_pacchetto(instance):
	esistenza_pacchetto_obj = Pacchetti.objects.filter(utente = instance, attivato = False).exists()
	if esistenza_pacchetto_obj:

		pacchetto_obj = Pacchetti.objects.get(utente = instance)
		giorni = pacchetto_obj.giorni

		now = datetime.now()
		scadenza = now + timedelta(giorni)

		pacchetto_obj.attivato = True
		pacchetto_obj.data_sottoscrizione = now
		pacchetto_obj.data_scadenza = scadenza
		pacchetto_obj.save()


def abbonamento_valido(instance):
	pacchetto_obj = Pacchetti.objects.get(utente = instance)
			
	now = date.today()
	data_scadenza = pacchetto_obj.data_scadenza

	if now > data_scadenza:
		return False #Abbonamento scaduto
	else:
		return True #Abbonamento valido


def estendi_scadenza(instance, giorni):
	pacchetto_obj = Pacchetti.objects.get(utente = instance, attivato = True)
	data_scadenza = pacchetto_obj.data_scadenza

	pacchetto_obj.data_scadenza = data_scadenza + timedelta(giorni)
	pacchetto_obj.save()


def percentuale_tempo_rimanente(instance):
	pacchetto_obj = Pacchetti.objects.get(utente = instance)

	now = date.today()
	data_scadenza = pacchetto_obj.data_scadenza

	delta_scadenza = data_scadenza - now  
	delta_scadenza = float(delta_scadenza.days)
	giorni_totali = float(pacchetto_obj.giorni)

	return 100-((delta_scadenza/giorni_totali)*100)


def get_dati_pacchetto(instance):
	esistenza = Pacchetti.objects.filter(utente = instance).exists()
	if esistenza:
		pacchetto_obj = Pacchetti.objects.get(utente = instance)

		now = date.today()
		data_scadenza = pacchetto_obj.data_scadenza

		if data_scadenza is None:
			giorni_totali = pacchetto_obj.giorni
			return 0, giorni_totali
		else:
			delta_scadenza = data_scadenza - now  
			delta_scadenza = delta_scadenza.days

			giorni_totali = pacchetto_obj.giorni

			return delta_scadenza, giorni_totali
	else:
		return 0,0


@login_required(login_url='/login')
def charge(request):

	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')

	esistenza = Pacchetti.objects.filter(utente = instance).exists()

	if esistenza:
		valido = abbonamento_valido(instance)

		if valido:
			return HttpResponse("package_exists")
		else:
			pack_obk = Pacchetti.objects.get(utente = instance)
			pack_obk.delete()

	#stripeEmail = request.POST['stripeEmail']	
	stripeToken = request.POST['stripeToken']
	piano = request.POST['piano']

	if piano == "pagamento_15":
		amount = 499
		giorni = 15
	elif piano == "pagamento_30":
		amount = 799
		giorni = 30
	elif piano == "pagamento_90":
		amount = 1999
		giorni = 90

	stripe.Charge.create(
	  amount = amount,
	  currency = "USD",
	  card = stripeToken, 
	  description = "Charge for Instautomation.com",
	)

	nuovo_pacchetto(instance, giorni)

	return HttpResponse()

class pay_tweet(View):
    template_name = 'riscatta.html'

    @method_decorator(login_required(login_url='/login'))
    def dispatch(self, *args, **kwargs):
        return super(pay_tweet, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
	
    def post(self, request, *args, **kwargs):
    	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')

    	user_obj = Utente.objects.get(utente = instance)

    	if user_obj.tweet_boolean:
    		return HttpResponse()
    	else:
    		user_obj.tweet_boolean = True
    		user_obj.save()

    		nuovo_pacchetto(instance, 1)
    		return HttpResponse()

@shared_task
def cron_scadenza_pacchetto(request):
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

	return HttpResponse(2)