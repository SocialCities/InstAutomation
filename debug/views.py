from django.shortcuts import render
from instagram_like.models import ListaTag
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required


@login_required(login_url='/login')
def aggiungi_like_debug(request):
	
	lista_tag = ['motivation', 'motivationshare', 'quote', 'dailymotivation', 'quoteoftheday', 'quotestoliveby', 'quotesgram', 'quotestags', 'quotesoftheday', 'quotesaboutlife', 'motivational', 'motivationmonday', 'motivationalmonday', 'motivationalquote', 'motivationforfitness', 'bestquotes', 'funnyquotes', 'funnyquote', 'inspirationalquotes', 'friendshipquotes', 'quotesandsaying', 'lovequotes', 'lifequotes', 'quotations']
	
	for singolo_tag in lista_tag:
		nuovo_tag = Tag(testo = singolo_tag)
		nuovo_tag.save()
	
	return HttpResponse(42)

