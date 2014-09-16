from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.views.generic import View

from instagram_like.models import ListaTag, BlacklistFoto, LikeTaskStatus
from instagram_like.forms import TagForm
from instagram_follow.models import UtentiRivali, FollowTaskStatus
from instagram_follow.forms import CercaCompetitorForm
from .decorators import task_non_completati

from celery.result import AsyncResult
from celery.task.control import revoke

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

MIOIP = "213.174.182.251"
	
def index(request):	
	return render_to_response('instalogin.html', context_instance=RequestContext(request))
	
def uscita(request):
    logout(request)
    return HttpResponseRedirect('/access') 	

def access(request):
    return HttpResponseRedirect('/home') 	    

class beta_home(View):
    template_name = 'beta_home.html'
    codice_beta = "pota"

    def dispatch(self, *args, **kwargs):
        return super(beta_home, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
	
    def post(self, request, *args, **kwargs):   
		beta_code = request.POST['beta_code'] 
		if beta_code == self.codice_beta: 
			request.session['in_beta'] = True   
			return HttpResponseRedirect('/home')
		else:
			return HttpResponseRedirect('/beta/')	

@login_required(login_url='/')
@task_non_completati
def home_page(request):	
	return render_to_response('index.html')	

class task_esistente(View):
    template_name = 'task_esistente.html'

    @method_decorator(login_required(login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(task_esistente, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
		
		instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
		
		follow_task_attivi = FollowTaskStatus.objects.filter(completato = False, utente = instance).exists()
		like_task_attivi = LikeTaskStatus.objects.filter(completato = False, utente = instance).exists()	

		if(follow_task_attivi is not True) and (like_task_attivi is not True):
			return HttpResponseRedirect('/home')
		else:			
			return render(request, self.template_name)
	
    def post(self, request, *args, **kwargs):
		instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	  	
		follow_task_attivi = FollowTaskStatus.objects.filter(completato = False, utente = instance).exists()
		like_task_attivi = LikeTaskStatus.objects.filter(completato = False, utente = instance).exists()
		
		if follow_task_attivi:
			task_attivo = FollowTaskStatus.objects.get(completato = False, utente = instance)
			task_id = task_attivo.task_id
			task_attivo.completato = True
			task_attivo.save()
			revoke(task_id, terminate=True, signal="KILL")	
			
		if like_task_attivi:
			like_attivo = LikeTaskStatus.objects.get(completato = False, utente = instance)
			task_id = like_attivo.task_id
			like_attivo.completato = True
			like_attivo.save()
			revoke(task_id, terminate=True, signal="KILL")	
        
		return HttpResponseRedirect('/home')

@login_required(login_url='/')
def follow_home(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']	
	template = loader.get_template('follow_home.html')
	
	cerca_competitor_form = CercaCompetitorForm()
	cerca_competitor_form.fields['username'].label = 'Cerca un competitor'
	
	rivali = UtentiRivali.objects.filter(utente = instance) 	

	api = InstagramAPI(
			access_token = access_token,
			client_ips = MIOIP,
			client_secret = "e42bb095bdc6494aa351872ea17581ac"
	)	
	
	context = RequestContext(request, {
		'rivali' : rivali,
		'form' : cerca_competitor_form,
	})
		
	return HttpResponse(template.render(context))	
	
@login_required(login_url='/')	
def like_home(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']	
	template = loader.get_template('like_home.html')
		
	lista_tag = ListaTag.objects.filter(utente = instance) 	
	form = TagForm()

	api = InstagramAPI(
			access_token = access_token,
			client_ips = MIOIP,
			client_secret = "e42bb095bdc6494aa351872ea17581ac"
	)	
	
	context = RequestContext(request, {
		'lista_tag' : lista_tag,
		'form' : form,
	})
		
	return HttpResponse(template.render(context))	
