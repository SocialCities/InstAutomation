from django.db import models
from social_auth.models import UserSocialAuth


class BlacklistUtenti(models.Model):
	username = models.CharField(max_length=200)	
	id_utente = models.CharField(max_length=200)	
	utente = models.ForeignKey(UserSocialAuth)
	unfollowato = models.NullBooleanField()
	time_stamp = models.DateTimeField(null = True, blank = True, auto_now_add=True)	
	
	def __unicode__(self):
		return self.username
	
	class Meta:
		
		index_together = [
			["id_utente", "utente"],
		]
		
		verbose_name = "Utente in blacklist"
		verbose_name_plural = "Utenti in blacklist"	
		
class WhitelistUtenti(models.Model):
	username = models.CharField(max_length=200)	
	id_utente = models.CharField(max_length=200)	
	utente = models.ForeignKey(UserSocialAuth)
	
	def __unicode__(self):
		return self.username
	
	class Meta:
		
		index_together = [
			["id_utente", "utente"],
		]
		
		verbose_name = "Utente in whitelist"
		verbose_name_plural = "Utenti in whitelist"			
		

class UtentiRivali(models.Model):
	username = models.CharField(max_length=200)	
	id_utente = models.CharField(max_length=200)	
	utente = models.ForeignKey(UserSocialAuth)		
	numero_follower = models.IntegerField()
	
	def __unicode__(self):
		return self.username
	
	class Meta:
		verbose_name = "Utente rivale"
		verbose_name_plural = "Utenti rivali"	
