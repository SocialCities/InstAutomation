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
				
# Foto da non likeare perche' gia' likeate
class BlacklistFoto(models.Model):
	id_foto = models.CharField(max_length=200)	
	link_foto = models.CharField(max_length=200)
	utente = models.ForeignKey(UserSocialAuth)
	
	def __unicode__(self):
		return self.link_foto
	
	class Meta:
		verbose_name = "Foto in blacklist"
		verbose_name_plural = "Foto in blacklist"	
		
		
class LikeTaskStatus(models.Model):
	task_id = models.CharField(max_length=300)
	completato = models.NullBooleanField()
	utente = models.ForeignKey(UserSocialAuth)
	
	def __unicode__(self):
		return str(self.task_id)
	
	class Meta:
		verbose_name = "Like task status"
		verbose_name_plural = "Like task status"
	
