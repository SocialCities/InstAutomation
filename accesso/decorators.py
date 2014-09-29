from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response

from social_auth.models import UserSocialAuth
from .models import Utente

def token_error(function):
  def wrap(request, *args, **kwargs):

        instance = UserSocialAuth.objects.get(user=request.user, provider='instagram')
        utente_obj = Utente.objects.get(utente = instance)
        token_block = utente_obj.token_block
        
        if token_block:
			return render(request, 'token_page.html')
        else:
			return function(request, *args, **kwargs)

  wrap.__doc__=function.__doc__
  wrap.__name__=function.__name__
  return wrap
