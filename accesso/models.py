from django.db import models
from social_auth.models import UserSocialAuth


class Utente(models.Model):
	utente = models.ForeignKey(UserSocialAuth)
	follower_iniziali = models.IntegerField()
	email = models.EmailField(null = True, blank=True)
	time_stamp = models.DateTimeField(null = True, blank = True, auto_now_add = True)	
	token_block = models.NullBooleanField(null = True, blank=True, default = False)
	like_totali = models.IntegerField(default = 0)
	like_sessione = models.IntegerField(default = 0)
	follow_totali = models.IntegerField(default = 0)
	follow_sessione = models.IntegerField(default = 0)
	data_blocco_forzato = models.DateField(null = True, blank = True)	
	tweet_boolean = models.NullBooleanField(default = False)
	lingua = models.CharField(max_length = 3, default = 'en')
	
	class Meta:
		verbose_name = "Dati dell'utente"
		verbose_name_plural = "Dati dell'utente"		

class TaskStatus(models.Model):
	task_id = models.CharField(max_length=300)
	completato = models.NullBooleanField()
	utente = models.ForeignKey(UserSocialAuth)
	sorgente = models.CharField(max_length=300)
	
	class Meta:
		verbose_name = "Task status"
		verbose_name_plural = "Task status"

class ValDelay(models.Model):
	delay_min = models.IntegerField()
	delay_max = models.IntegerField()

	class Meta:
		verbose_name = "Valore delay"
		verbose_name_plural = "Valore delay"	