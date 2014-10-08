from __future__ import absolute_import

from django.conf import settings
from celery import shared_task
from celery.task.schedules import crontab
from celery.decorators import periodic_task

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

@periodic_task(run_every=(crontab(minute=0, hour=0)))
def elimina_vecchi_utenti():
    now = datetime.now()
    
    tre_giorni_fa = now - timedelta(3)
	
    utenti_da_eliminare = BlacklistUtenti.objects.filter(unfollowato = True, time_stamp__lt = tre_giorni_fa)
    utenti_da_eliminare.delete()
    print 42

    
