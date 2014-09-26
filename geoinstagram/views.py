from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI
from django.conf import settings

MIOIP = settings.IP_LOCALE
CLIENT_SECRET = settings.INSTAGRAM_CLIENT_SECRET

@login_required(login_url='/')
def localize(request):
	template = loader.get_template('localizzami.html')
	
	context = RequestContext(request)
		
	return HttpResponse(template.render(context))	
	
@login_required(login_url='/')
def mappa(request):
	
	latitudine = request.GET.get('lat')
	longitudine = request.GET.get('lng')
	
	instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
	access_token = instance.tokens['access_token']
	
	api = InstagramAPI(
        access_token = access_token,
        client_ips = MIOIP,
        client_secret = CLIENT_SECRET 
    )
	
	media_vicini = api.media_search(lat = latitudine, lng = longitudine, count = 100, distance = 5000)	
	
	#for media in media_vicini:
		#print media.user.username
	#	point_obj = media.location.point
	#	latitude = point_obj.latitude
	#	longitude = point_obj.longitude
	
	template = loader.get_template('map.html')
	
	context = RequestContext(request, {
		'media_vicini': media_vicini,
		"centroLat" : latitudine,
		"centroLng" : longitudine,		
	})
		
	return HttpResponse(template.render(context))	
