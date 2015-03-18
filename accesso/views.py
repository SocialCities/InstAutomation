# -*- coding: utf-8 -*-

from django.shortcuts import render
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
from instagram_follow.models import UtentiRivali
from instagram_follow.tasks import avvia_task_pulizia_follower
from pagamenti.models import Pacchetti
from pagamenti.views import nuovo_pacchetto, attiva_pacchetto, abbonamento_valido, estendi_scadenza, get_dati_pacchetto
from instagram_like.views import nuovi_tag

from .models import Utente, TaskStatus
from .tasks import start_task, invio_email_primo_avvio
from .decorators import token_error
from instautomation.utility import errore_mortale

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError

from instautomation.utility  import kill_all_tasks
from postmonkey import PostMonkey


MIOIP = settings.IP_LOCALE
CLIENT_SECRET = settings.INSTAGRAM_CLIENT_SECRET
	
from django.utils import translation	
def index(request):
	template_name = "instalogin.html"

	numero_iscritti = Utente.objects.filter().count()
	
	#linguaggio = request.META['LANGUAGE']
	linguaggio = translation.get_language_from_request(request)

	if linguaggio == 'it':	
		welcome = "Benvenuto su Instautomation"
		sub_welcome = '<p>Un nuovo modo per <span class="hue coloured">ottimizzare</span> le funzioni di Instagram!</p>'
		start_now = 'INIZIA ORA GRATIS!'
		small_credits = '<i>Usando Instautomation, accetti i nostri <a href="javascript:openTerms()">termini di servizio</a> e la nostra <a href="//www.iubenda.com/privacy-policy/203721" class="iubenda-nostyle no-brand iubenda-embed" title="Privacy Policy">privacy policy</a></i>'
		titolo_target = "L'importanza del <span class='hue coloured'>TARGET</span>"
		corpo_target = 'Instautomation lavora in maniera <span class="hue coloured">intelligente</span>: utilizza i giusti <span class="hue coloured">target</span> ed <span class="hue coloured">hashtag</span> per portare più traffico al tuo profilo ed aumentare i tuoi <span class="hue coloured">follower</span>.'
		titolo_plan = 'Scegli la <span class="hue coloured">TUA</span> offerta!'
		corpo_plan = 'Il servizio è <span class="hue coloured">gratuito</span> per due giorni dalla tua iscrizione. Se la prova gratis soddisfa le tue esigenze, potrai scegliere uno dei nostri <span class="hue coloured">tre</span> differenti pacchetti.'
		termini = 'Termini di servizio'
		privacy = 'Privacy'
		chiudi = 'Chiudi'
		torna_in_cima = 'Torna in cima'
		iubenda_link = '//www.iubenda.com/privacy-policy/578901'
	elif linguaggio == 'ro':
		welcome = "Bine ați venit pe Instautomation!"
		sub_welcome = '<p>Un nou mod de a <span class="hue coloured">optimiza</span> utilizarea programului Instagram!</p>'
		start_now = 'INCEPE ACUMA GRATIS!'
		small_credits = '<i>Utilizand Instautomation accepți condițiile de utilizare și politica de privacy</i>'
		titolo_target = '<span class="hue coloured">Targetul</span> conteaza!'
		corpo_target = 'Instautomation lucreaza în mod <span class="hue coloured">inteligent</span>: utilizeaza targetul și <span class="hue coloured">hashtagul potrivit</span> pentru a aduce mai mult trafic de persoane interesate de <span class="hue coloured">profilul</span> tau și face sa-ți creasca numarul de Followers.'
		titolo_plan = 'Alege <span class="hue coloured">oferta</span> potrivita!'
		corpo_plan = 'Serviciu este <span class="hue coloured">gratuit</span> pentru primele doua zile. Daca proba gratis satisface dorințele tale, poți să alegi una dintre cele <span class="hue coloured">trei</span> propuneri oferite de noi.'
		termini = 'Termeni'
		privacy = 'Confidenţialitate'
		chiudi = 'Închide'
		torna_in_cima = 'Back to top' 
		iubenda_link = '//www.iubenda.com/privacy-policy/203721'
	elif linguaggio == "fr":
		welcome = "Soyez les bienvenus sur Instautomation!"
		sub_welcome = "C’est une nouvelle façon <span class='hue coloured'>d'optimiser</span> les fonctions de l'Instagram"
		start_now = 'COMMENCE MAINTENANT GRATUITEMENT!'
		small_credits = '<i>Aide Instautomation, vous acceptez <a href="javascript:openTerms()">les conditions d’utilisation</a> et notre <a href="//www.iubenda.com/privacy-policy/203721" class="iubenda-nostyle no-brand iubenda-embed" title="politique de confidentialité">privacy policy</a></i>'		
		titolo_target = "La <span class='hue coloured'>cible</span> est essentielle!"
		corpo_target = "L'Instautomation travaille d'une manière <span class='hue coloured'>intelligente</span>: il utilise la <span class='hue coloured'>cible</span> et les <span class='hue coloured'>hashtags</span> convenables pour attirer plus de gens qui sont intéressés par votre profil et faire augmenter le nombre d’adeptes de <span class='hue coloured'>followers</span>."
		titolo_plan = "Choisissez l'offre qui <span class='hue coloured'>vous</span> convient!"
		corpo_plan = "Le service est <span class='hue coloured'>gratuit</span> pour les premiers deux jours. Si l'échantillon gratuit correspond à vos attentes, vous pouvez choisir l’une des <span class='hue coloured'>trois</span> offres, que nous mettons à votre disposition."
		termini = "Conditions d'utilisation"
		privacy = 'Confidentialité'
		chiudi = 'Fermer'
		torna_in_cima = 'Retour au sommet!'
		iubenda_link = '//www.iubenda.com/privacy-policy/203721'				
	else:
		welcome = "Welcome to Instautomation!"
		sub_welcome = 'A new way that provide <span class="hue coloured">optimization</span> for Instagram.'
		start_now = 'START NOW FOR FREE!'
		small_credits = '<i>By using Instautomation, you agree to the <a href="javascript:openTerms()">Terms of Service</a> and <a href="//www.iubenda.com/privacy-policy/203721" class="iubenda-nostyle no-brand iubenda-embed" title="Privacy Policy">Privacy Policy</a><script type="text/javascript" src="//cdn.iubenda.com/iubenda_i_badge.js"></script></i>'
		titolo_target = '<span class="hue coloured">TARGETING</span> MATTERS.'
		corpo_target = 'Instautomation works in a <span class="hue coloured">smart</span> way. Using <span class="hue coloured">precise hashtags</span> and the <span class="hue coloured">right target</span> you can increase the number of your followers.'
		titolo_plan = 'CHOOSE THE <span class="hue coloured">BEST</span> FOR YOU.'
		corpo_plan = 'You start with the <span class="hue coloured">free trial</span> for two days, than, if you are satisfied by our service, you can choose one of our <span class="hue coloured">three</span> different packs.'
		termini = 'Our terms'
		privacy = 'Privacy'
		chiudi = 'Close'
		torna_in_cima = 'Back to top'
		iubenda_link = '//www.iubenda.com/privacy-policy/203721'		

	variabili = {
	'numero_iscritti' : numero_iscritti, 
	'welcome' : welcome, 
	'sub_welcome' : sub_welcome,
	'start_now' : start_now,
	'small_credits' : small_credits,
	'titolo_target' : titolo_target,
	'corpo_target' : corpo_target,
	'titolo_plan' : titolo_plan,
	'corpo_plan' : corpo_plan,
	'termini' : termini,
	'privacy' : privacy,
	'chiudi' : chiudi,
	'torna_in_cima' : torna_in_cima,
	'iubenda_link' : iubenda_link
	}

	return render(request, template_name, variabili)
	
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
		
		try:
			informazioni = api.user()

		except InstagramAPIError as errore:
			errore_mortale(errore, instance) 

		followed_by = informazioni.counts['followed_by']

		#linguaggio = request.META['LANGUAGE']
		linguaggio = translation.get_language_from_request(request)
		if linguaggio == 'it':
			lingua = 'it'
		elif linguaggio == 'ro':
			lingua = 'ro'
		elif linguaggio == "fr":
			lingua = "fr"
		else:
			lingua = 'en'

		nuove_stats = Utente(utente = instance, follower_iniziali = followed_by, lingua = lingua)
		nuove_stats.save()
		
		nuovo_pacchetto(instance, 2)

		nuovi_tag(instance)
		
		return HttpResponseRedirect('/')   
		
class beta_home(View):
    template_name = 'beta_home.html'
    codice_beta = "betapene"

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

	try:
		me_object = api.user()
	except InstagramAPIError as errore:		
		errore_mortale(errore, instance)
		return HttpResponseRedirect('/')

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
	lingua = user_obj.lingua
	followers_at_registration = user_obj.follower_iniziali
	follower_since_registration = followed_by - followers_at_registration 

	lista_tag = ListaTag.objects.filter(utente = instance) 
	rivali = UtentiRivali.objects.filter(utente = instance)

	# Inizio sezione status pacchetti
	esistenza_pacchetto = Pacchetti.objects.filter(utente = instance).exists()
	if esistenza_pacchetto:
		pacchetto_attivato = Pacchetti.objects.filter(utente = instance, attivato = True).exists()
		if pacchetto_attivato:

			if abbonamento_valido(instance):
				stato_pacchetto = 2 #Abbonamento valido 
				time_remaining, giorni_totali = get_dati_pacchetto(instance) 
			else:
				stato_pacchetto = 1 #Abbonamento scaduto
				time_remaining, giorni_totali = get_dati_pacchetto(instance)
				time_remaining = 0
		else:
			stato_pacchetto = 3 #Pacchetto non usato ma valido
			time_remaining, giorni_totali = get_dati_pacchetto(instance)
	else:
		giorni_totali = 0
		stato_pacchetto = 0	
		time_remaining = 0
	# Fine sezione status pacchetti
	
	#Sezione che gestisce gli avvisi. Di base non ho avvisi.
	avviso = None

	if(data_blocco is not None):
		if(stato_pacchetto == 3):
			user_obj.data_blocco_forzato = None
			user_obj.save()		

		elif(stato_pacchetto == 2):			
			now = date.today()
			delta_data_blocco = now - data_blocco
			giorni = delta_data_blocco.days

			if giorni == 0:
				giorni = 1

				if lingua == 'it':
					testo_regalo = "un giorno in più di utilizzo"
				elif lingua == 'ro':
					testo_regalo = "O zi în plus"
				elif lingua == "fr":
					testo_regalo = "un jour en plus d'utilisation"
				else:
					testo_regalo = "one more free day"
			else:
				giorni = giorni + 1

				if lingua == 'it':
					testo_regalo = str(giorni) + ' giorni in più di utilizzo'
				elif lingua == "ro":
					testo_regalo = str(giorni) + ' zile în plus'
				elif lingua == "fr":
					testo_regalo = str(giorni) + ' plus jours'
				else:
					testo_regalo = str(giorni) + ' more free days'					

			if lingua == 'it':
				avviso = "Gentile utente, purtroppo il sistema si è bloccato per ragioni inaspettate. Ti abbiamo regalato "+testo_regalo+". Ci scusiamo per il disagio."
			elif lingua == "ro":
				avviso = "Dragă utiizator, din pacate sistemul sa blocat. Iți facem cadou încă"+testo_regalo+". Ne scuzam pentru disconfort."
			elif lingua == "fr":
				avviso = "Gentil utilisateur, le système s'est malheurosement bloqué puor raisons inattendues. On t'ai offert "+testo_regalo+". Veuillez nous excuser pour les troubles occasionnés."
			else:
				avviso = 'Dear user, unfortunately the system was blocked for unknown reasons. Your account has been enlarged with '+testo_regalo+'. Sorry for the inconvenience'
			
			estendi_scadenza(instance, giorni)
			time_remaining, giorni_totali = get_dati_pacchetto(instance)
			user_obj.data_blocco_forzato = None
			user_obj.save()

		elif(stato_pacchetto == 1):
			pacchetto_obj = Pacchetti.objects.get(utente = instance, attivato = True)
			data_scadenza = pacchetto_obj.data_scadenza

			if data_blocco > data_scadenza:
				user_obj.data_blocco_forzato = None
				user_obj.save()
			else:
				delta_data_blocco = data_scadenza - data_blocco
				giorni = delta_data_blocco.days

				if giorni == 1:
					if lingua == 'it':
						testo_regalo = "un giorno in più di utilizzo"
					elif lingua == 'ro':
						testo_regalo = "O zi în plus"
					elif lingua == "fr":
						testo_regalo = "un jour en plus d'utilisation"	
					else:
						testo_regalo = "one more free day"					
				else:
					giorni = giorni + 1

					if lingua == 'it':
						testo_regalo = str(giorni) + ' giorni in più di utilizzo'
					elif lingua == "ro":
						testo_regalo = str(giorni) + ' zile în plus'
					elif lingua == "fr":
						testo_regalo = str(giorni) + ' plus jours'												
					else:
						testo_regalo = str(giorni) + ' more free days'	
				
				if lingua == 'it':
					avviso = "Gentile utente, purtroppo il sistema si è bloccato per ragioni inaspettate. Ti abbiamo regalato "+testo_regalo+". Ci scusiamo per il disagio."
				elif lingua == "ro":
					avviso = "Dragă utiizator, din pacate sistemul sa blocat. Iți facem cadou încă"+testo_regalo+". Ne scuzam pentru disconfort."
				elif lingua == "fr":
					avviso = "Gentil utilisateur, le système s'est malheurosement bloqué puor raisons inattendues. On t'ai offert "+testo_regalo+". Veuillez nous excuser pour les troubles occasionnés."
				else:
					avviso = 'Dear user, unfortunately the system was blocked for unknown reasons. Your account has been enlarged with '+testo_regalo+'. Sorry for the inconvenience'

				user_obj.data_blocco_forzato = None
				user_obj.save()
				pacchetto_obj.delete()
				nuovo_pacchetto(instance, giorni)
				time_remaining, giorni_totali = get_dati_pacchetto(instance)
				stato_pacchetto = 3
	######################################################################					

	like_totali = user_obj.like_totali
	follow_totali = user_obj.follow_totali

	if(giorni_totali == 2) and (stato_pacchetto == 3):
		if lingua == 'it':
			warning_string = 'Ciao!'
			avviso = "Puoi iniziare ad usare Instautomation gratuitamente per due giorni!<br/>\
			1) Aggiungi uno o più utenti target con i contenuti simili ai tuoi<br/>\
			2) Scegli qualche hashtag su cui fare like (te ne abbiamo già inseriti un paio)<br/>\
			3) Premi START!"
		elif lingua == "fr":
			warning_string = 'Salut!'
			avviso = "Tu peux commencer à utiliser Instautomation gratuitement pour deux jours!<br/>\
			1) Ajoutez un utilisateur target avec les contenus semblables aux tiens<br/>\
			2) Choisissez quelques hashtag sur lequel faire like (nous avons déjà insérés quelqu’un)<br/>\
			3) Presser START!"
		elif lingua == "ro":
			warning_string = 'Salut!'
			avviso = "Puteți utiliza Instautomation gratis pentru doua zile!<br/>\
			1) Adăuga un utilizator target cu interese similare<br/>\
			2) Alege hashtaguri potrivit(v-am sugerat câteva)<br/>\
			3) Apasă START!"			
		else:
			warning_string = 'Hi!'
			avviso = "You can start using Instautomation free for two days!<br/>\
			1) Add an user target  who has your similar contents.<br/>\
			2) Choose some hastag to autolike (we give you a couple!)<br/>\
			3) Push START!"			
	else:
		if lingua == 'it':
			warning_string = 'Attenzione!'
		elif lingua == "ro":
			warning_string = "Attenție!"
		elif lingua == "fr":
			warning_string = "Avertissement!"	
		else:
			warning_string = 'Warning!'			

	status_obj_attivi = TaskStatus.objects.filter(utente = instance, completato = False).exists()	

	if lingua == 'it':
		info_label = "Info"
		my_profile_label = "My profile"
		corpo_choose_target_profile_string = "Cerca e seleziona profili influenti come marchi leader, VIP o persone che rispecchiano i tuoi interessi."
		corpo_choose_tag_string = "Aggiungi i tag più popolari o che utilizzi spesso nelle tue foto"
		modale_titolo_email_obbligatoria = "Ancora un attimo..."
		modale_corpo_email_obbligatoria = "Abbiamo bisogno della tua email per poterti contattare in caso di bisogno"
		sistema_attivo_string = "Il sistema è attivo!"
		string_js_15_giorni = 'Entry Pack - 15 giorni'
		string_js_30_giorni = 'Standard Pack - 30 giorni'
		string_js_90_giorni = 'Power Pack - 90 giorni'
		invia_string = "Invia"
		prezzi = "Prezzi"
		termini = 'Termini di servizi'
		privacy = 'Privacy'
		supporto = 'Supporto'
		cambia_email = 'Cambia indirizzo email'
		logout = 'Logout'
		post_string = 'Post'
		follower_string = 'Follower'
		following_string = 'Following'
		nuovi_seguaci_string = 'nuovi followers dalla registrazione'
		elapsed_time_string = 'Tempo trascorso'
		pause_string = 'PAUSA'
		avvia_string = 'START'
		total_time_string = 'Tempo totale acquistato'
		giorni_string = 'giorni'
		tempo_restante_string = 'Tempo restante'
		comprato_string = 'Comprato'
		rimanenti_string = 'Rimasto'
		compra_pacchetto_string = 'Per usare il sistema devi acquistare un nuovo pacchetto di giorni!'
		time_over_string = 'Hai esaurito il tempo'
		avviso_partenza_string = 'Una volta premuto il pulsante di avvio, il tempo inizierà a scorrere, e non sarà possibile fermarlo fino alla sua conclusione.'
		settings_title = 'Targets & Tags'
		target_users_title = 'Utenti target'
		search_placeholder = 'Cerca un utente target'
		ricerca_string = 'Cerca'
		selected_users_string = 'Utenti selezionati'
		selected_tags_string = "Tag selezionati"
		tags_string = 'Tag'
		salva_sting = 'Salva'
		subscription_bonus_string = 'Bonus di benvenuto'
		giorni_free_subscription_string = "2 giorni in regalo all'iscrizione"
		pay_tweet_string = 'Pay with a Tweet'
		corpo_pay_tweet = 'Paga con un tweet e ricevi un giorno di utilizzo in regalo'
		un_giorno_free_string = '1 giorno gratis'
		gia_preso_string = 'Già effettuato!'
		string_15_giorni_titolo = '15 giorni a &euro;6.99'
		entry_pack_string = 'Entry Pack'
		string_15_giorni = '15 giorni'
		prezzo_15_giorni = '&euro;6.99'
		paga_card_string = 'Paga con carta'
		titolo_30_giorni = '30 giorni a &euro;10.79'
		standard_pack_string = 'Standard Pack'
		string_30_giorni = '30 giorni'
		prezzo_30_giorni = '&euro;10.79'
		titolo_90_giorni_string = '90 giorni a &euro;24.49'
		power_pack_string = 'Power Pack'
		stringa_90_giorni = '90 giorni'
		prezzo_90_giorni_string = '&euro;24.49'
		stringa_iva_inclusa = 'Prezzi IVA inclusa.'
		accettazione_termini_string = 'Accettazione dei termini'
		you_have_to_accept = 'Devi accettare i termini di servizio e inserire un indirizzo email per continuare.'		
		conferma_lettura_string = 'Ho letto i termini e acconsento alle condizioni *'
		continua_string = 'Continua'
		aiuto_string = 'Hai bisogno di aiuto?'
		titolo_string_supporto = 'Titolo *'
		placeholder_titolo_supporto_string = 'Titolo'
		messaggio_string_support = 'Messaggio *'
		write_a_message_placeholder = 'Scrivi un messaggio'
		chiudi_string = 'Chiudi'
		cambia_email_string = 'Cambia indirizzo email'
		email_attuale_string = 'La tua email è'
		nuova_email_string = 'Nuova email *'
		placeholder_nuova_email = 'Inserisci la nuova email'
		conferma_nuova_email = 'Ripeti la nuova email *'
		conferma_email_string_placeholder = 'Conferma il tuo indirizzo email'
		errore_corpo_modale_string = '<p>Qualcosa è andato storto!<br/>Perfavore, riprova tra poco.<br/>Per informazioni scrivici a info@instautomation.com</p>'		
		errore_numero_tag_e_target = 'Per iniziare ad usare il sistema devi inserire almeno un utente target e almeno un hashtag'
		caricamento_string = 'Caricamento...'
		torna_in_cima = 'Torna in cima'
		no_target_found_string = 'Nessun utente target trovato'
		utente_esiste_string = 'Target già inserito!'
		added_generico_string = 'Fatto!'
		tag_esistente_string = 'Tag già inserito'
		choose_target_profile_string = 'Aggiungi uno o più utenti target'
		choose_tag_string = 'Scegli qualche hashtag'
		your_account_string = "Il tuo account"
		il_tuo_abbonamento_string = "I tuoi dati"
		il_sistema_ha_generato = "Statistiche"
		utenti_stringa = 'utenti'
		seguiti_dal_sistema_string = 'seguiti dal sistema'
		liked_by_system_string = 'likeati dal sistema'
		titolo_pagamenti_string = "Aumenta i giorni"
		aumenta_giorni_string = 'Aumenta i giorni!'
		errore_myself_string = "Non puoi scegliere te stesso come target!"
		num_tag_modal_string = "Una parola alla volta!"
		insert_a_tag_place = 'Inserisci un TAG'
		lingua_string = 'Lingua'
		iubenda_link = '//www.iubenda.com/privacy-policy/578901'
		benvenuto_avatar_string = 'Benvenuto'
		email_string = "Email"
	elif lingua == 'ro':
		my_profile_label = "My profile"
		info_label = "Info"
		corpo_choose_target_profile_string = "Caută și selecționeaza profile interesante tip un brand lider, VIP sau persoane interesate de aceleași lucruri ca și tine." 
		corpo_choose_tag_string = "Adaugă tag-utile mai populare sau care le folosești des in pozele tale." 
		modale_titolo_email_obbligatoria = "Încă un pic..."
		modale_corpo_email_obbligatoria = "Avem nevoie de adresa ta de email pentru a-te contacta în caz de necesitate"		
		sistema_attivo_string = "Sistemul este activ!"
		string_js_15_giorni = 'Entry Pack - 15 zile'
		string_js_30_giorni = 'Standard Pack - 30 zile'
		string_js_90_giorni = 'Power Pack - 90 zile'
		invia_string = "Trimite"
		prezzi = "Prețuri"
		termini = 'Termeni'
		privacy = 'Confidențialitate'
		supporto = 'Ajutor'
		cambia_email = 'Schimba adresa de email'
		logout = 'Logout'
		post_string = 'Posts'
		follower_string = 'Followers'
		following_string = 'Following'
		nuovi_seguaci_string = 'Followers obținuți dupa registrare'
		elapsed_time_string = 'Timp utilizat'
		pause_string = 'PAUSA'
		avvia_string = 'START'
		total_time_string = 'Timp total'
		giorni_string = 'zile'
		tempo_restante_string = 'Timp rămas'
		comprato_string = 'Cumparat'
		rimanenti_string = 'Rămas'
		compra_pacchetto_string = 'Pentru a utiliza sistemul trebuie să cumperi un nou pachet de zile!'
		time_over_string = 'Ai gatat timpul la dispoziție'
		avviso_partenza_string = 'După apăsarea butonului START, incepe timpul la dispoziție, nu se opreste până cănd nu scade.'
		settings_title = 'Targets & Tags'
		target_users_title = 'Utilizatorii target'
		search_placeholder = 'Caută un utilizator target'
		ricerca_string = 'Caută'
		selected_users_string = 'Utilizatorii lezați'
		selected_tags_string = "Tag selectați"
		tags_string = 'Tags'
		salva_sting = 'Salvează'
		subscription_bonus_string = 'Bonus de bun venit'
		giorni_free_subscription_string = '2 zile cadou de la înregistrare'
		pay_tweet_string = 'Pay with a Tweet'
		corpo_pay_tweet = 'Platește cu un Tweet și vei primi o zi de utilizare cadou'
		un_giorno_free_string = 'O zi gratis'
		gia_preso_string = 'Deja făcut!'
		string_15_giorni_titolo = '15 zile la &euro;6.99'
		entry_pack_string = 'Entry Pack'
		string_15_giorni = '15 zile'
		prezzo_15_giorni = '&euro;6.99'
		paga_card_string = 'Platește cu cardul'
		titolo_30_giorni = '30 zile la &euro;10.79'
		standard_pack_string = 'Standard Pack'
		string_30_giorni = '30 zile'
		prezzo_30_giorni = '&euro;10.79'
		titolo_90_giorni_string = '90 zile la &euro;24.49'
		power_pack_string = 'Power Pack'
		stringa_90_giorni = '90 zile'
		prezzo_90_giorni_string = '&euro;24.49'
		stringa_iva_inclusa = 'Prețuri TVA inclus.'
		accettazione_termini_string = 'Acceptați condițiile de utilizare'
		you_have_to_accept = 'Acceptați condițiile de utilizare și introduceți adresa de e-mail pentru a continua'
		conferma_lettura_string = 'Am citit, și accept condițiile de utilizare *'
		continua_string = 'Continuă'
		aiuto_string = 'Ai nevoie de ajutor?'
		titolo_string_supporto = 'Titlu *'
		placeholder_titolo_supporto_string = 'Titlu'
		messaggio_string_support = 'Mesaj *'
		write_a_message_placeholder = 'Scrie un mesaj'
		chiudi_string = 'Închide'
		cambia_email_string = 'Schimbă adresa de email'
		email_attuale_string = 'Adresa ta de email este'
		nuova_email_string = 'Noua adresa de email *'
		placeholder_nuova_email = 'introduceți o noua adresa de email'
		conferma_nuova_email = 'Repetă noua adresa de email *'
		conferma_email_string_placeholder = 'Confirmare noua adresa de email'
		errore_corpo_modale_string = '<p>Ceva a mers prost!<br/>Vă rugăm să încercați din nou mai târziu.<br/>Pentru informați: info@instautomation.com</p>'		
		errore_numero_tag_e_target = 'Pentru a utiliza serviciul introduceți un utilizator target sau un hashtag'
		caricamento_string = 'Încărcare...'
		torna_in_cima = 'Back to top'
		no_target_found_string = 'Nici un utilizator target găsit'
		utente_esiste_string = 'Target deja folosit!'
		added_generico_string = 'Terminat!'
		tag_esistente_string = 'Tag deja folosit'
		choose_target_profile_string = 'Adaugă unul sau mai mulți utilizatori' 
		choose_tag_string = 'Alege un hashtag' 
		your_account_string = "Accountul tau"
		il_tuo_abbonamento_string = "Datele tale"
		il_sistema_ha_generato = "Statistice"
		utenti_stringa = 'utilizatorii'
		seguiti_dal_sistema_string = 'Utilizatorii urmariți prin sistem'
		liked_by_system_string = 'likeați prin sistem'
		titolo_pagamenti_string = "Cumpăra mai multe zile"
		aumenta_giorni_string = 'Adaugă alte zile!'
		errore_myself_string = "Nu poți să te alegi pe tine ca și target!"
		num_tag_modal_string = "Câte un cuvânt pe rând!"
		insert_a_tag_place = 'introduceți un TAG'
		lingua_string = 'Limbă'
		iubenda_link = '//www.iubenda.com/privacy-policy/203721'
		benvenuto_avatar_string = 'Bine ai venit'
		email_string = "Email"
	elif lingua == 'fr':
		my_profile_label = "My profile"
		info_label = "Info"
		corpo_choose_target_profile_string = "Recherche et sélectionne profils influents comme des marques leader, VIP ou gens qu'ils reflètent tes intérêts." 
		corpo_choose_tag_string = "Ajoute les tag les plus populaires ou que tu utilises souvent dans tes photos"
		sistema_attivo_string = " Le système est actif!"
		string_js_15_giorni = 'Entry Pack - 15 jours'
		string_js_30_giorni = 'Standard Pack - 30 jours'
		string_js_90_giorni = 'Power Pack - 90 jours'
		invia_string = "Envoie"
		prezzi = "Prix"
		termini = "Conditions d'utilisation"
		privacy = 'Confidentialité'
		supporto = 'Soutien'
		cambia_email = 'Change ton adresse email'
		logout = 'Logout'
		post_string = 'Post'
		follower_string = 'Follower'
		following_string = 'Following'
		nuovi_seguaci_string = "nouveaux followers de l'enregistrement"
		elapsed_time_string = 'Temps passé'
		pause_string = 'PAUSE'
		avvia_string = 'START'
		total_time_string = 'Temps total acheté'
		giorni_string = 'jours'
		tempo_restante_string = 'Temps reste'
		comprato_string = 'Acheté'
		rimanenti_string = 'Reste'
		compra_pacchetto_string = 'Pour utiliser le système tu dois acheter un nouveau paquet de jours!'
		time_over_string = 'Tu as épuisé le temps'
		avviso_partenza_string = "Une fois pressée le bouton de commencement, le temps commencera à couler, et il ne sera pas possible de l'arrêter jusqu'à la sa conclusion."
		settings_title = 'Targets & Tags'
		target_users_title = 'Utilisateurs target'
		search_placeholder = 'Cherche un utilisateur target'
		ricerca_string = 'Cherche'
		selected_users_string = 'Utilisateurs sélectionnés'
		selected_tags_string = "Tags sélectionnés"
		tags_string = 'Tag'
		salva_sting = 'Sauver'
		subscription_bonus_string = 'Bonus de bienvenu'
		giorni_free_subscription_string = "2 jours en cadeau à l'inscription"
		pay_tweet_string = 'Pay with a Tweet'
		corpo_pay_tweet = 'Paie avec un tweet et tu reçois un jour de jouissance en cadeau'
		un_giorno_free_string = '1 jour gratis'
		gia_preso_string = 'Déjà effectué!'
		string_15_giorni_titolo = '15 jours a &euro;6.99'
		entry_pack_string = 'Entry Pack'
		string_15_giorni = '15 jours'
		prezzo_15_giorni = '&euro;6.99'
		paga_card_string = 'Paye par carte de crédit'
		titolo_30_giorni = '30 jours a &euro;10.79'
		standard_pack_string = 'Standard Pack'
		string_30_giorni = '30 jours'
		prezzo_30_giorni = '&euro;10.79'
		titolo_90_giorni_string = '90 jours a &euro;24.49'
		power_pack_string = 'Power Pack'
		stringa_90_giorni = '90 jours'
		prezzo_90_giorni_string = '&euro;24.49'
		stringa_iva_inclusa = 'Prix TVA incluse.'
		accettazione_termini_string = 'Acceptation des conditions d’utilisation'
		you_have_to_accept = 'Tu dois accepter les termes de service et saisir une adresse email pour continuer.'		
		conferma_lettura_string = "J'ai lu les termes et je consens aux conditions *"
		continua_string = 'Continue'
		aiuto_string = "Tu as besoin d'aide?"
		titolo_string_supporto = 'Titre *'
		placeholder_titolo_supporto_string = 'Titre'
		messaggio_string_support = 'Message *'
		write_a_message_placeholder = 'Ècrivez un messagge'
		chiudi_string = 'Fermer' 
		cambia_email_string = 'Change ton adresse email'
		email_attuale_string = 'Ton adresse email est'
		nuova_email_string = 'Nouvelle adresse email*'
		placeholder_nuova_email = 'Saisissez la nouvelle adresse email'
		conferma_nuova_email = 'Répètes la nouvelle adresse email *'
		conferma_email_string_placeholder = 'Confirmes votre adresse email'
		errore_corpo_modale_string = '<p>Quelque chose est allé de travers!<br/>S’il vous plait, veulles réessayer plus tard.<br/>Pour avoir des information écris-nous à info@instautomation.com</p>'		
		errore_numero_tag_e_target = 'Pour commencer à utiliser le système tu dois insérer au moins un utilisateur target et au moins un hashtag'
		caricamento_string = 'Chargement...'
		torna_in_cima = 'Retour au sommet!'
		no_target_found_string = 'Aucun utilisateur target trouvé'
		utente_esiste_string = 'Target déjà inséré!'
		added_generico_string = 'Fait!'
		tag_esistente_string = 'Tag déjà inséré '
		choose_target_profile_string = 'Ajoute un ou plus utilisateurs target' 
		choose_tag_string = 'Choisis quelques hashtag' 
		your_account_string = "Ton account"
		il_tuo_abbonamento_string = "Tes données"
		il_sistema_ha_generato = "Statistique"
		utenti_stringa = ' utilisateurs '
		seguiti_dal_sistema_string = 'suivi par le système'
		liked_by_system_string = 'like par le système'
		titolo_pagamenti_string = "Augmentez les jours"
		aumenta_giorni_string = "Augmentez les jours!"
		errore_myself_string = "Tu ne peux pas choisir tu même comme target !"
		num_tag_modal_string = " Un mot à la fois!"
		insert_a_tag_place = 'Insérez un TAG'
		lingua_string = 'Langue'
		iubenda_link = '//www.iubenda.com/privacy-policy/203721'
		benvenuto_avatar_string = 'Bienvenu'
		email_string = "Email"
		modale_titolo_email_obbligatoria = "Une dernière chose..."	
		modale_corpo_email_obbligatoria = "Nous avons besoin de ton adresse email pour pouvoir t'avertir en cas de problèmes"				
	else:
		my_profile_label = "My profile"
		info_label = "Info"
		corpo_choose_target_profile_string = "Search and select influent profiles like important brand, VIP or people that have the same interests as you." 
		corpo_choose_tag_string = "Add the most popular tags or the ones that you use in your photos more frequently" 
		modale_titolo_email_obbligatoria = "One more thing..."
		modale_corpo_email_obbligatoria = "We need your email address to contact you in case of problems"		
		sistema_attivo_string = "System is running!"
		string_js_15_giorni = 'Entry Pack - 15 Days'
		string_js_30_giorni = 'Standard Pack - 30 Days'
		string_js_90_giorni = 'Power Pack - 90 Days'
		invia_string = "Send"
		prezzi = "Prices"
		termini = 'Our terms'
		privacy = 'Privacy'
		supporto = 'Support'
		cambia_email = 'Change my email'
		logout = 'Logout'
		post_string = 'Posts'
		follower_string = 'Followers'
		following_string = 'Following'
		nuovi_seguaci_string = 'new followers since your registration!'
		elapsed_time_string = 'Elapsed time'
		pause_string = 'PAUSE'
		avvia_string = 'START'
		total_time_string = 'Total time bought'
		giorni_string = 'days'
		tempo_restante_string = 'Time remaining'
		comprato_string = 'Bought'
		rimanenti_string = 'Left'
		compra_pacchetto_string = 'To use the system you have to buy a new package!'
		time_over_string = 'Your time is over!'
		avviso_partenza_string = 'Once the start button has been hit, time will start to decrease, ad it will not be possible to stop it until it is completely drained.'
		settings_title = 'Targets & Tags'
		target_users_title = 'Target users'
		search_placeholder = 'Search a target user'
		ricerca_string = 'Search'
		selected_users_string = 'Selected users'
		selected_tags_string = "Selected tags"
		tags_string = 'Tags'
		salva_sting = 'Save'
		subscription_bonus_string = 'Subscrition bonus'
		giorni_free_subscription_string = '2 free days for every new account!'
		pay_tweet_string = 'Pay with a Tweet'
		corpo_pay_tweet = 'Pay with a tweet and get another free day for your account'
		un_giorno_free_string = '1 free day'
		gia_preso_string = 'Already redeemed!'
		string_15_giorni_titolo = '15 days for &euro;6.99'
		entry_pack_string = 'Entry Pack'
		string_15_giorni = '15 days'
		prezzo_15_giorni = '&euro;6.99'
		paga_card_string = 'Pay with card'
		titolo_30_giorni = '30 days for &euro;10.79'
		standard_pack_string = 'Standard Pack'
		string_30_giorni = '30 days'
		prezzo_30_giorni = '&euro;10.79'
		titolo_90_giorni_string = '90 days for &euro;24.49'
		power_pack_string = 'Power Pack'
		stringa_90_giorni = '90 days'
		prezzo_90_giorni_string = '&euro;24.49'
		stringa_iva_inclusa = 'All prices are VAT included.'
		accettazione_termini_string = 'Acceptance of terms'
		you_have_to_accept = 'You have to accept terms and insert you email address to continue.'
		conferma_lettura_string = 'I have read this Agreement and I agree to the terms and conditions *'
		continua_string = 'Continue'
		aiuto_string = 'Need help?'
		titolo_string_supporto = 'Subject *'
		placeholder_titolo_supporto_string = 'Subject'
		messaggio_string_support = 'Message *'
		write_a_message_placeholder = 'Write a message'
		chiudi_string = 'Close'
		cambia_email_string = 'Change email address'
		email_attuale_string = 'Your current email is'
		nuova_email_string = 'New email *'
		placeholder_nuova_email = 'Insert a new email'
		conferma_nuova_email = 'Repeat email *'
		conferma_email_string_placeholder = 'Confirm your email'
		errore_corpo_modale_string = '<p>Something went wrong!<br/>Please, try in a while.<br/>For support contact us at info@instautomation.com</p>'
		errore_numero_tag_e_target = 'To start the system you must insert at least one target user and one hashtag.'
		caricamento_string = 'LOADING...'
		torna_in_cima = 'Back to top'
		no_target_found_string = 'No target users found'
		utente_esiste_string = 'This user already exists!'
		added_generico_string = 'Added!'
		tag_esistente_string = 'This tag exists'
		choose_target_profile_string = 'Add one or more users target'
		choose_tag_string = 'Choose some hashtags'
		your_account_string = "Your account"
		il_tuo_abbonamento_string = "Your subscription"
		il_sistema_ha_generato = "Statistics"
		utenti_stringa = 'users'
		seguiti_dal_sistema_string = 'followed by the system'
		liked_by_system_string = 'liked by the system'
		titolo_pagamenti_string = "Buy more days!"
		aumenta_giorni_string = 'Increase your days!'
		errore_myself_string = "You can't add yourself as a target!"
		num_tag_modal_string = "One word at a time please!"
		insert_a_tag_place = 'Insert a TAG'
		lingua_string = 'Language'
		iubenda_link = '//www.iubenda.com/privacy-policy/203721'
		benvenuto_avatar_string = 'Welcome'
		email_string = "Email"

	variabili = {
		'my_profile_label' : my_profile_label,
		'info_label' : info_label,
		'corpo_choose_target_profile_string' : corpo_choose_target_profile_string,
		'corpo_choose_tag_string' : corpo_choose_tag_string,
		'email_string' : email_string,
		'modale_titolo_email_obbligatoria' : modale_titolo_email_obbligatoria,
		'modale_corpo_email_obbligatoria' : modale_corpo_email_obbligatoria,
		'sistema_attivo_string' : sistema_attivo_string,
		'string_js_15_giorni' : string_js_15_giorni,
		'string_js_30_giorni' : string_js_30_giorni,
		'string_js_90_giorni' : string_js_90_giorni,
		'invia_string' : invia_string,
		'termini' : termini,
		'privacy' : privacy,
		'prezzi' : prezzi,
		'supporto' : supporto,
		'cambia_email' : cambia_email,
		'logout' : logout,
		'post_string' : post_string,
		'follower_string' : follower_string,
		'following_string' : following_string,
		'warning_string' : warning_string,
		'nuovi_seguaci_string' : nuovi_seguaci_string,
		'elapsed_time_string' : elapsed_time_string,
		'pause_string' : pause_string,
		'avvia_string' : avvia_string,
		'total_time_string' : total_time_string,
		'giorni_string' : giorni_string,
		'tempo_restante_string' : tempo_restante_string,
		'comprato_string' : comprato_string,
		'rimanenti_string' : rimanenti_string,
		'compra_pacchetto_string' : compra_pacchetto_string,
		'time_over_string' : time_over_string,
		'avviso_partenza_string' : avviso_partenza_string,
		'settings_title' : settings_title,
		'target_users_title' : target_users_title,
		'search_placeholder' : search_placeholder,
		'ricerca_string' : ricerca_string,
		'selected_users_string' : selected_users_string,
		'tags_string' : tags_string,
		'salva_sting' : salva_sting,
		'subscription_bonus_string' : subscription_bonus_string,
		'giorni_free_subscription_string' : giorni_free_subscription_string,
		'pay_tweet_string' : pay_tweet_string,
		'corpo_pay_tweet' : corpo_pay_tweet,
		'un_giorno_free_string' : un_giorno_free_string,
		'gia_preso_string' : gia_preso_string,
		'string_15_giorni_titolo' : string_15_giorni_titolo,
		'entry_pack_string' : entry_pack_string,
		'string_15_giorni' : string_15_giorni,
		'prezzo_15_giorni' : prezzo_15_giorni,
		'paga_card_string' : paga_card_string,
		'titolo_30_giorni' : titolo_30_giorni,
		'standard_pack_string' : standard_pack_string,
		'string_30_giorni' : string_30_giorni,
		'prezzo_30_giorni' : prezzo_30_giorni,
		'titolo_90_giorni_string' : titolo_90_giorni_string,
		'power_pack_string' : power_pack_string,
		'stringa_90_giorni' : stringa_90_giorni,
		'prezzo_90_giorni_string' : prezzo_90_giorni_string,
		'stringa_iva_inclusa' : stringa_iva_inclusa,
		'accettazione_termini_string' : accettazione_termini_string,
		'you_have_to_accept' : you_have_to_accept,
		'conferma_lettura_string' : conferma_lettura_string,
		'continua_string' : continua_string,
		'aiuto_string' : aiuto_string,
		'titolo_string_supporto' : titolo_string_supporto,
		'placeholder_titolo_supporto_string' : placeholder_titolo_supporto_string,
		'messaggio_string_support' : messaggio_string_support,
		'write_a_message_placeholder' : write_a_message_placeholder,
		'chiudi_string' : chiudi_string,
		'cambia_email_string' : cambia_email_string,
		'email_attuale_string' : email_attuale_string,
		'nuova_email_string' : nuova_email_string,
		'placeholder_nuova_email' : placeholder_nuova_email,
		'conferma_nuova_email' : conferma_nuova_email,
		'conferma_email_string_placeholder' : conferma_email_string_placeholder,
		'errore_corpo_modale_string' : errore_corpo_modale_string,
		'errore_numero_tag_e_target' : errore_numero_tag_e_target,
		'caricamento_string' : caricamento_string,
		'torna_in_cima' : torna_in_cima,
		'no_target_found_string' : no_target_found_string,
		'utente_esiste_string' : utente_esiste_string,
		'added_generico_string' : added_generico_string,
		'selected_tags_string' : selected_tags_string,
		'tag_esistente_string' : tag_esistente_string,
		'choose_target_profile_string' : choose_target_profile_string,
		'choose_tag_string' : choose_tag_string,
		'your_account_string' : your_account_string,
		'il_tuo_abbonamento_string' : il_tuo_abbonamento_string,
		'il_sistema_ha_generato' : il_sistema_ha_generato,
		'like_totali' : like_totali,
		'follow_totali' : follow_totali,
		'utenti_stringa' : utenti_stringa,
		'seguiti_dal_sistema_string' : seguiti_dal_sistema_string,
		'liked_by_system_string' : liked_by_system_string,
		'titolo_pagamenti_string' : titolo_pagamenti_string,
		'aumenta_giorni_string' : aumenta_giorni_string,
		'status_obj_attivi' : status_obj_attivi,
		'errore_myself_string' : errore_myself_string,
		'num_tag_modal_string' : num_tag_modal_string,
		'insert_a_tag_place' : insert_a_tag_place,
		'lingua_string' : lingua_string,
		'iubenda_link' : iubenda_link,
		'benvenuto_avatar_string' : benvenuto_avatar_string,

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
		'time_remaining' : time_remaining,
		'giorni_totali' : giorni_totali,
		'tweet_boolean' : tweet_boolean,
		'avviso' : avviso
		}	
		
	context = RequestContext(request, variabili)

	return HttpResponse(template.render(context)) 	

@login_required(login_url='/login')
def ferma_task(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	kill_all_tasks(instance)
	
	return HttpResponse()		

@login_required(login_url='/login')
def avvia_task(request):	
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']	

	esistenza_rivali = UtentiRivali.objects.filter(utente = instance).exists()
	esisteza_tag = ListaTag.objects.filter(utente = instance).exists()

	if esistenza_rivali and esisteza_tag:
	
		user_obj = Utente.objects.get(utente = instance)
		user_obj.like_sessione = 0
		user_obj.follow_sessione = 0
		user_obj.save()
		
		result = start_task.delay(access_token, instance)		
		id_task = result.task_id		
		nuovo_task = TaskStatus(task_id = id_task, completato = False, utente = instance, sorgente = "accesso")
		nuovo_task.save()

		esistenza_pacchetto_da_attivare = Pacchetti.objects.filter(utente = instance, attivato = False)
		if esistenza_pacchetto_da_attivare:
			attiva_pacchetto(instance)

		return HttpResponse()
	else:
		return HttpResponse('no_resources')


@login_required(login_url='/login')
def clean(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']		

	esistenza = TaskStatus.objects.filter(completato = False, utente = instance, sorgente = "unfollow").exists()
	
	if esistenza:
		return HttpResponseRedirect('/')
	else:
		result = avvia_task_pulizia_follower.delay(access_token, instance, True, None)		
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

	email_utente = user_obj.email
	if email_utente == email:
		return HttpResponse("exists")
	else:
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
		errore = 'Please insert your email.<br />'
	else:
		email_da_controllare = request.POST['email']	
		f = forms.EmailField()
		try:
			f.clean(email_da_controllare)
		except:
			errore = 'Please insert a valid email.<br />'
	
	if (richiesta.__contains__('message') is False):
		errore = 'Please insert a message.<br />'		
	else:
		if len(request.POST['message']) < 10:
			errore = 'Your message should have at least 10 chars.<br />'		
	
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


def email_chimp(request):
	email = request.POST['email']
	apikey = 'a36024c7bb5504d63b61963dd9741fa2-us8'
	mailid = 'c4ed436de6'

	pm = PostMonkey(apikey)
	pm.listSubscribe(id = mailid, email_address = email, double_optin = False)
	return HttpResponse()

@login_required(login_url='/login')
def change_lang(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')

	lingua = request.POST['lingua']

	Utente.objects.filter(utente = instance).update(lingua = lingua)
	return HttpResponse()


@login_required(login_url='/login')
def salva_email(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')

	email = request.POST['email']

	try:
		apikey = 'a36024c7bb5504d63b61963dd9741fa2-us8'
		mailid = 'c4ed436de6'

		pm = PostMonkey(apikey)
		pm.listSubscribe(id = mailid, email_address = email, double_optin = False)
	except:
		pass

	Utente.objects.filter(utente = instance).update(email = email)
	return HttpResponse()