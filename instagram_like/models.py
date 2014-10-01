from django.db import models
from django import forms
from social_auth.models import UserSocialAuth

# Tag di quote o motivation
class ListaTag(models.Model):
	keyword = models.CharField(max_length=200)
	utente = models.ForeignKey(UserSocialAuth)
	
	def __unicode__(self):
		return self.keyword
	
	class Meta:
		verbose_name = "Tag"
		verbose_name_plural = "Tag"		
				
