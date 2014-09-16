from django.db import models
from social_auth.models import UserSocialAuth

# Create your models here.

class trackStats(models.Model):
	utente = models.ForeignKey(UserSocialAuth)
	follower_iniziali = models.IntegerField()	
	
	def __unicode__(self):
		return self.utente
	
	class Meta:
		verbose_name = "Statistiche iniziali"
		verbose_name_plural = "Statistiche iniziali"	
