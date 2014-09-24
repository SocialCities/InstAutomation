from __future__ import absolute_import

from django.conf import settings
from celery import shared_task

from social_auth.models import UserSocialAuth
from instagram.client import InstagramAPI

from .models import TaskStatus

import logging
logger = logging.getLogger('django')

from InstaTrezzi.utility import check_limite

MIOIP = settings.IP_LOCALE

from instagram_like.tasks import insta_task
from instagram_follow.tasks import how_i_met_your_follower


@shared_task   
def start_task(token, instance):
	res1 = insta_task.delay(token, instance)	
	res2 = how_i_met_your_follower.delay(token, instance, '1439702168')
	
	id_task1 = res1.task_id
	id_task2 = res2.task_id
	
	nuovo_task1 = TaskStatus(task_id = id_task1, completato = False, utente = instance)
	nuovo_task1.save()
	
	nuovo_task2 = TaskStatus(task_id = id_task2, completato = False, utente = instance)
	nuovo_task2.save()
	
		
	return 'yo'
