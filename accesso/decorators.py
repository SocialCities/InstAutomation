from social_auth.models import UserSocialAuth
from instagram_like.models import LikeTaskStatus
from instagram_follow.models import FollowTaskStatus

from django.http import HttpResponseRedirect


def task_non_completati(function):
  def wrap(request, *args, **kwargs):
        instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')	
	  	
        follow_task_attivi = FollowTaskStatus.objects.filter(completato = False, utente = instance).exists()
        like_task_attivi = LikeTaskStatus.objects.filter(completato = False, utente = instance).exists()

        if (follow_task_attivi is True) or (like_task_attivi is True):
			
			return HttpResponseRedirect('/task_esistente')
        else:
            return function(request, *args, **kwargs)

  wrap.__doc__=function.__doc__
  wrap.__name__=function.__name__
  return wrap
