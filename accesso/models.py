from django.db import models
from social_auth.models import UserSocialAuth

# Create your models here.
	
class Utente(models.Model):
	utente = models.ForeignKey(UserSocialAuth)
	follower_iniziali = models.IntegerField()
	email = models.EmailField(null = True, blank=True)
	time_stamp = models.DateTimeField(null = True, blank = True, auto_now_add=True)	
	token_block = models.NullBooleanField(null = True, blank=True, default = False)
	
	class Meta:
		verbose_name = "Dati dell'utente"
		verbose_name_plural = "Dati dell'utente"		

class TaskStatus(models.Model):
	task_id = models.CharField(max_length=300)
	completato = models.NullBooleanField()
	utente = models.ForeignKey(UserSocialAuth)
	
	def __unicode__(self):
		return str(self.task_id)
	
	class Meta:
		verbose_name = "Task status"
		verbose_name_plural = "Task status"
	
