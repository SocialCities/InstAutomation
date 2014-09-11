from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

from .models import UtentiRivali
from .forms import CercaCompetitorForm, RivaliForm

@login_required(login_url='/')
def cerca_competitor(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	access_token = instance.tokens['access_token']	
	
	cerca_competitor_form = CercaCompetitorForm(request.GET)
	if cerca_competitor_form.is_valid():
		nome_da_cercare = cerca_competitor_form.cleaned_data['username']
	
	api = InstagramAPI(
        access_token=access_token,
        client_ips="82.106.24.34",
        client_secret="e42bb095bdc6494aa351872ea17581ac"
    )
    
	rivali = UtentiRivali.objects.filter(utente = instance) 	
	cerca_competitor_form = CercaCompetitorForm()
	cerca_competitor_form.fields['username'].label = 'Cerca un competitor'
	
	tutti_nomi = api.user_search(q = nome_da_cercare)	
					
	template = loader.get_template('follow_home_ricerca.html')
	context = RequestContext(request, {
		'tutti_nomi': tutti_nomi,		
		'rivali' : rivali,
		'form' : cerca_competitor_form,
	})
		
	return HttpResponse(template.render(context))
	


@login_required(login_url='/')
def aggiungi_competitor(request):
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	rivale_form = RivaliForm(request.POST)
		
	if rivale_form.is_valid():
		username = rivale_form.cleaned_data['username']
		id_utente = rivale_form.cleaned_data['id_utente']
		nuovo_rivale = UtentiRivali(username = username, id_utente = id_utente, utente = instance)
		nuovo_rivale.save()
						
	return HttpResponseRedirect('/follow')      	

