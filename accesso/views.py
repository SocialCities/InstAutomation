from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.generic import View
from django.conf import settings
from django import forms

from datetime import date

from instagram_like.models import ListaTag
from instagram_like.forms import TagForm
from instagram_follow.models import UtentiRivali
from instagram_follow.forms import CercaCompetitorForm
from instagram_follow.tasks import avvia_task_pulizia_follower
from pagamenti.models import Pacchetti
from pagamenti.views import nuovo_pacchetto, attiva_pacchetto, abbonamento_valido

from .models import Utente, TaskStatus
from .tasks import start_task
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
    return HttpResponseRedirect('/access') 	

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
	template = loader.get_template('home_page.html')
	
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

	
	user_obj = Utente.objects.get(utente = instance)
	email_salavata = user_obj.email
	numero_like_totali = user_obj.like_totali
	numero_follow = user_obj.follow_totali
	
	if status_obj_attivi is False:
		numero_like_sessione = 0
		numero_follow_sessione = 0
	else:
		numero_like_sessione = user_obj.like_sessione
		numero_follow_sessione = user_obj.follow_sessione
	
	context = RequestContext(request, {
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
	})
		
	return HttpResponse(template.render(context))	
	
@login_required(login_url='/login')
def cerca_competitor(request):	
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']	
	
	cerca_competitor_form = CercaCompetitorForm(request.GET)
	if cerca_competitor_form.is_valid():
		nome_da_cercare = cerca_competitor_form.cleaned_data['username']
	
	template = loader.get_template('home_page_rivali.html')
	
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
	
	user_obj = Utente.objects.get(utente = instance)
	email_salavata = user_obj.email
	numero_like_totali = user_obj.like_totali
	numero_follow = user_obj.follow_totali

	if status_obj_attivi is False:
		numero_like_sessione = 0
		numero_follow_sessione = 0
	else:
		numero_like_sessione = user_obj.like_sessione
		numero_follow_sessione = user_obj.follow_sessione
	
	api = InstagramAPI(
			access_token = access_token,
			client_ips = MIOIP,
			client_secret = CLIENT_SECRET 
	)		
	
	tutti_nomi = api.user_search(q = nome_da_cercare)	
	
	new_tutti_nomi = []
	
	for nome in tutti_nomi[:10]:
		try:
			followed_by = api.user(nome.id).counts['followed_by']
			nome.followed_by = followed_by
			new_tutti_nomi.append(nome)
		except:
			pass
		
	new_tutti_nomi = sorted(new_tutti_nomi, key = lambda user_obj: user_obj.followed_by, reverse=True)
	
	altri_nomi = tutti_nomi[10:]
	
	context = RequestContext(request, {
		'rivali' : rivali,
		'competitor_form' : cerca_competitor_form,
		'lista_tag' : lista_tag,
		'tag_form' : tag_form,
		'tutti_nomi' : new_tutti_nomi,
		'altri_nomi' : altri_nomi,
		'status_obj_attivi' : status_obj_attivi,
		'numero_follow' : numero_follow,
		'numero_like_totali' : numero_like_totali,
		'numero_like_sessione' : numero_like_sessione,
		'numero_follow_sessione' : numero_follow_sessione,
		'email_salavata' : email_salavata,
		'stato_pacchetto' : stato_pacchetto,
	})
		
	return HttpResponse(template.render(context))	

@login_required(login_url='/login')
def ferma_task(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	kill_all_tasks(instance)
			
	return HttpResponseRedirect('/')

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

	return HttpResponseRedirect('/')


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
	try:
		email = f.clean(email_da_controllare)
		instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
		
		user_obj = Utente.objects.get(utente = instance)
		user_obj.email = email
		user_obj.save()
	
		return HttpResponseRedirect('/')
	except:
		return HttpResponse("Inserisci una email")		
