from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.generic import View
from django.conf import settings
from django import forms

from datetime import date
from django.core.mail import EmailMultiAlternatives 

from instagram_like.models import ListaTag
from instagram_like.forms import TagForm
from instagram_follow.models import UtentiRivali
from instagram_follow.forms import CercaCompetitorForm
from instagram_follow.tasks import avvia_task_pulizia_follower
from pagamenti.models import Pacchetti
from pagamenti.views import nuovo_pacchetto, attiva_pacchetto, abbonamento_valido, estendi_scadenza, percentuale_tempo_rimanente, get_dati_pacchetto

from .models import Utente, TaskStatus
from .tasks import start_task, invio_email_primo_avvio
from .decorators import token_error

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

from instautomation.utility  import kill_all_tasks

MIOIP = settings.IP_LOCALE
CLIENT_SECRET = settings.INSTAGRAM_CLIENT_SECRET
	
def index(request):	
	return render_to_response('instalogin.html', context_instance=RequestContext(request))
	
def uscita(request):
    logout(request)
    return HttpResponseRedirect('/login') 	

def access(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']
	
	esistenza_track = Utente.objects.filter(utente = instance).exists()
    
	if esistenza_track:
		
		user_obj = Utente.objects.get(utente = instance)
		user_obj.token_block = False
		user_obj.save()		
		
		return HttpResponseRedirect('/')
		
	else:				
		api = InstagramAPI(
				access_token = access_token,
				client_ips = MIOIP,
				client_secret = CLIENT_SECRET
		)
		
		informazioni = api.user()			
		followed_by = informazioni.counts['followed_by']
		nuove_stats = Utente(utente = instance, follower_iniziali = followed_by)
		nuove_stats.save()
		
		nuovo_pacchetto(instance, 2)
		
		return HttpResponseRedirect('/')   
		
class beta_home(View):
    template_name = 'beta_home.html'
    codice_beta = "Xyiu753!qa4?"

    def dispatch(self, *args, **kwargs):
        return super(beta_home, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
	
    def post(self, request, *args, **kwargs):   
		beta_code = request.POST['beta_code'] 
		if beta_code == self.codice_beta: 
			request.session['in_beta'] = True   
			return HttpResponseRedirect('/')
		else:
			return HttpResponseRedirect('/beta/')			
			
	
@login_required(login_url='/login')
@token_error
def home_page(request):	
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']	

	template = loader.get_template('index.html')

	api = InstagramAPI(
				access_token = access_token,
				client_ips = MIOIP,
				client_secret = CLIENT_SECRET
	)

	me_object = api.user()

	username = me_object.username
	avatar = me_object.profile_picture
	me_counts = me_object.counts
	num_post = me_counts['media']
	followed_by = me_counts['followed_by']
	follows = me_counts['follows']

	user_obj = Utente.objects.get(utente = instance)
	data_blocco = user_obj.data_blocco_forzato
	tweet_boolean = user_obj.tweet_boolean
	email = user_obj.email
	followers_at_registration = user_obj.follower_iniziali
	follower_since_registration = followed_by - followers_at_registration 

	lista_tag = ListaTag.objects.filter(utente = instance) 
	rivali = UtentiRivali.objects.filter(utente = instance)
	percentuale_tempo = 0

	#Status pacchetti
	esistenza_pacchetto = Pacchetti.objects.filter(utente = instance).exists()
	if esistenza_pacchetto:
		pacchetto_attivato = Pacchetti.objects.filter(utente = instance, attivato = True).exists()
		if pacchetto_attivato:

			if abbonamento_valido(instance):
				stato_pacchetto = 2 #Abbonamento valido
				percentuale_tempo = percentuale_tempo_rimanente(instance)  
				time_remaining, giorni_totali = get_dati_pacchetto(instance)           
			else:
				stato_pacchetto = 1 #Abbonamento scaduto
				time_remaining, giorni_totali = get_dati_pacchetto(instance)

		else:
			stato_pacchetto = 3 #Pacchetto non usato ma valido
			time_remaining, giorni_totali = get_dati_pacchetto(instance)
	else:
		giorni_totali = 0
		stato_pacchetto = 0	
		time_remaining = 0

	#Sezione che gestisce gli avvisi. Di base non ho avvisi impostati
	avviso = None

	if (stato_pacchetto == 2) and (data_blocco is not None):
		
		now = date.today()

		delta_data_blocco = now - data_blocco
		giorni = delta_data_blocco.days

		if giorni == 0:
			giorni = 1
			#testo_regalo = "un giorno"
			testo_regalo = "one more free day"
		else:
			giorni = giorni + 1
			#testo_regalo = str(giorni) +" giorni"		
			testo_regalo = str(giorni) + ' more free days'

		avviso = 'Dear user, unfortunately the system was blocked for unknown reasons. Your account has been enlarged with '+testo_regalo+'. Sorry for the inconvenience'
		#avviso = "Ciao! Il sistema e stato bloccato forzatamete, per farci perdonare ti abbiamo regalato " + testo_regalo +" in piu!"
		estendi_scadenza(instance, giorni)
		user_obj.data_blocco_forzato = None
		user_obj.save()

	if (stato_pacchetto == 1) and (data_blocco is not None):
		pacchetto_obj = Pacchetti.objects.get(utente = instance, attivato = True)
		data_scadenza = pacchetto_obj.data_scadenza

		if data_blocco > data_scadenza:
			user_obj.data_blocco_forzato = None
			user_obj.save()
		else:
			delta_data_blocco = data_scadenza - data_blocco
			giorni = delta_data_blocco.days

			if giorni == 1:
				#testo_regalo = "un giorno"
				testo_regalo = "one more free day"
			else:
				giorni = giorni + 1
				#testo_regalo = str(giorni) + " giorni"
				testo_regalo = str(giorni) + ' more free days'
			
			avviso = 'Dear user, unfortunately the system was blocked for unknown reasons. Your account has been enlarged with '+testo_regalo+'. Sorry for the inconvenience'
			#avviso = "Ciao! Prima che ti scadesse il sistema abbiamo bloccato forzatamente la baracca. Per farci perdonare ti abbiamo regalato un pacchetto da " + testo_regalo
			user_obj.data_blocco_forzato = None
			user_obj.save()
			pacchetto_obj.delete()
			nuovo_pacchetto(instance, giorni)
			stato_pacchetto = 3

	######################################################################		
	
	status_obj_attivi = TaskStatus.objects.filter(utente = instance, completato = False).exists()

	if status_obj_attivi is False:
		numero_like_sessione = 0
		numero_follow_sessione = 0
	else:
		numero_like_sessione = user_obj.like_sessione
		numero_follow_sessione = user_obj.follow_sessione

	context = RequestContext(request, {
		'username' : username,
		'avatar' : avatar,
		'num_post' : num_post,
		'followed_by' : followed_by,
		'follows' : follows,
		'follower_since_registration' : follower_since_registration,
		'lista_tag' : lista_tag,
		'rivali' : rivali,
		'email' : email,
		'stato_pacchetto' : stato_pacchetto,
		'percentuale_tempo' : percentuale_tempo,
		'time_remaining' : time_remaining,
		'giorni_totali' : giorni_totali,
		'status_obj_attivi' : status_obj_attivi,
		'numero_like_sessione' : numero_like_sessione,
		'numero_follow_sessione' : numero_follow_sessione,
		'tweet_boolean' : tweet_boolean,
		'avviso' : avviso,
	})

	return HttpResponse(template.render(context)) 	



#Deprecato

@login_required(login_url='/login')
@token_error
def home_page_old(request):	
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']	

	#template = loader.get_template('home_page.html')
	template = loader.get_template('index.html')

	api = InstagramAPI(
				access_token = access_token,
				client_ips = MIOIP,
				client_secret = CLIENT_SECRET
	)

	me_object = api.user()

	username = me_object.username
	avatar = me_object.profile_picture
	me_counts = me_object.counts
	num_post = me_counts['media']
	followed_by = me_counts['followed_by']
	follows = me_counts['follows']

	user_obj = Utente.objects.get(utente = instance)
	followers_at_registration = user_obj.follower_iniziali
	follower_since_registration = followed_by - followers_at_registration 

	cerca_competitor_form = CercaCompetitorForm()
	cerca_competitor_form.fields['username'].label = 'Cerca un competitor'
	
	rivali = UtentiRivali.objects.filter(utente = instance) 	
	
	lista_tag = ListaTag.objects.filter(utente = instance) 	
	tag_form = TagForm()
	
	status_obj_attivi = TaskStatus.objects.filter(utente = instance, completato = False).exists()

	esistenza_pacchetto = Pacchetti.objects.filter(utente = instance).exists()

	if esistenza_pacchetto:
		pacchetto_attivato = Pacchetti.objects.filter(utente = instance, attivato = True).exists()
		if pacchetto_attivato:

			if abbonamento_valido(instance):
				stato_pacchetto = 2 #Abbonamento valido
			else:
				stato_pacchetto = 1 #Abbonamento scaduto

		else:
			stato_pacchetto = 3 #Pacchetto non usato ma valido
	else:
		stato_pacchetto = 0
	
	
	email_salavata = user_obj.email
	numero_like_totali = user_obj.like_totali
	numero_follow = user_obj.follow_totali
	data_blocco = user_obj.data_blocco_forzato
	

	######################################################################
	#Zona avvisi blocchi importanti
	#Di base non ho avvisi impostati
	avviso = None

	if (stato_pacchetto == 2) and (data_blocco is not None):
		
		now = date.today()

		delta_data_blocco = now - data_blocco
		giorni = delta_data_blocco.days

		if giorni == 0:
			giorni = 1
			testo_regalo = "un giorno"
		else:
			giorni = giorni + 1
			testo_regalo = str(giorni) +" giorni"		

		avviso = "Ciao! Il sistema e stato bloccato forzatamete, per farci perdonare ti abbiamo regalato " + testo_regalo +" in piu!"
		estendi_scadenza(instance, giorni)
		user_obj.data_blocco_forzato = None
		user_obj.save()

	if (stato_pacchetto == 1) and (data_blocco is not None):
		pacchetto_obj = Pacchetti.objects.get(utente = instance, attivato = True)
		data_scadenza = pacchetto_obj.data_scadenza

		if data_blocco > data_scadenza:
			user_obj.data_blocco_forzato = None
			user_obj.save()
		else:
			delta_data_blocco = data_scadenza - data_blocco
			giorni = delta_data_blocco.days
			if giorni == 1:
				testo_regalo = "un giorno"
			else:
				giorni = giorni + 1
				testo_regalo = str(giorni) + " giorni"
			avviso = "Ciao! Prima che ti scadesse il sistema abbiamo bloccato forzatamente la baracca. Per farci perdonare ti abbiamo regalato un pacchetto da " + testo_regalo
			user_obj.data_blocco_forzato = None
			user_obj.save()
			pacchetto_obj.delete()
			nuovo_pacchetto(instance, giorni)
			stato_pacchetto = 3

	######################################################################		

	if status_obj_attivi is False:
		numero_like_sessione = 0
		numero_follow_sessione = 0
	else:
		numero_like_sessione = user_obj.like_sessione
		numero_follow_sessione = user_obj.follow_sessione		

	context = RequestContext(request, {
		'username' : username,
		'avatar' : avatar,
		'num_post' : num_post,
		'followed_by' : followed_by,
		'follows' : follows,
		'follower_since_registration' : follower_since_registration,

		'rivali' : rivali,
		'competitor_form' : cerca_competitor_form,
		'lista_tag' : lista_tag,
		'tag_form' : tag_form,
		'status_obj_attivi' : status_obj_attivi,
		'numero_follow' : numero_follow,
		'numero_like_totali' : numero_like_totali,
		'numero_like_sessione' : numero_like_sessione,
		'numero_follow_sessione' : numero_follow_sessione,
		'email_salavata' : email_salavata,
		'stato_pacchetto' : stato_pacchetto,
		'avviso' : avviso,
	})
		
	return HttpResponse(template.render(context))	
	
#Fine deprecazione

@login_required(login_url='/login')
def ferma_task(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	kill_all_tasks(instance)
	
	return HttpResponse()		

@login_required(login_url='/login')
def avvia_task(request):	
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']		
	
	user_obj = Utente.objects.get(utente = instance)
	user_obj.like_sessione = 0
	user_obj.follow_sessione = 0
	user_obj.save()
	
	result = start_task.delay(access_token, instance)
	
	id_task = result.task_id
	
	nuovo_task1 = TaskStatus(task_id = id_task, completato = False, utente = instance, sorgente = "accesso")
	nuovo_task1.save()

	esistenza_pacchetto_da_attivare = Pacchetti.objects.filter(utente = instance, attivato = False)
	if esistenza_pacchetto_da_attivare:
		attiva_pacchetto(instance)

	#return HttpResponseRedirect('/')
	return HttpResponse()


@login_required(login_url='/login')
def clean(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']		
	
	result = avvia_task_pulizia_follower.delay(access_token, instance, True)
	
	id_task = result.task_id
		
	nuovo_task = TaskStatus(task_id = id_task, completato = False, utente = instance, sorgente = "unfollow")
	nuovo_task.save()
		
	return HttpResponseRedirect('/')	
	
@login_required(login_url='/login')
def add_email(request):
	email_da_controllare = request.POST['email']
	f = forms.EmailField()
	
	email = f.clean(email_da_controllare)
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
		
	user_obj = Utente.objects.get(utente = instance)
	user_obj.email = email
	user_obj.save()

	username = user_obj.utente.extra_data['username']

	primo_avvio = request.POST['primo_avvio']

	if(primo_avvio == 'true'):
		invio_email_primo_avvio.delay(email, username)
	
	return HttpResponse('')	

@login_required(login_url='/login')
def contact_process(request):
	errore = ''
	
	richiesta = request.POST	

	if richiesta.__contains__('email') is False:
		errore = 'Per favore inserisci la tua email.<br />'
	else:
		email_da_controllare = request.POST['email']	
		f = forms.EmailField()
		try:
			f.clean(email_da_controllare)
		except:
			errore = 'Per favore inserisci un indirizzo email valido.<br />'
	
	if (richiesta.__contains__('message') is False):
		errore = 'Per favore inserisci un messaggio.<br />'		
	else:
		if len(request.POST['message']) < 10:
			errore = 'Il tuo messaggio dovrebbe avere almeno dieci caratteri.<br />'		
	
	if errore == '':		
		if richiesta.__contains__('subject'):
			subject = request.POST['subject']
		else:
			subject = "Info Instautomation"
				
		from_email = request.POST['email']
		to = 'info@instautomation.com'
		text_content = request.POST['message']
		html_content = request.POST['message']
		
		msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
		msg.attach_alternative(html_content, "text/html")
		msg.send()
		
		return HttpResponse('OK')
	else:
		return HttpResponse('<div class="notification_error">'+errore+'</div>')	