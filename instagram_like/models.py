from django.db import models
from social_auth.models import UserSocialAuth

class ListaTag(models.Model):
	keyword = models.CharField(max_length=200)
	utente = models.ForeignKey(UserSocialAuth)
	
	def __unicode__(self):
		return self.keyword
	
	class Meta:
		verbose_name = "Tag"
		verbose_name_plural = "Tag"					

class BlackTag(models.Model):
	utente = models.ForeignKey(UserSocialAuth)
	id_media = models.CharField(max_length=200)
	time_stamp = models.DateTimeField(auto_now_add=True)	

	def __unicode__(self):
		return self.id_media
	
	class Meta:
		verbose_name = "BlackTag"
		verbose_name_plural = "BlackTag"			