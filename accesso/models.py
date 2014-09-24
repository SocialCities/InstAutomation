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

class TaskStatus(models.Model):
	task_id = models.CharField(max_length=300)
	completato = models.NullBooleanField()
	utente = models.ForeignKey(UserSocialAuth)
	
	def __unicode__(self):
		return str(self.task_id)
	
	class Meta:
		verbose_name = "Task status"
		verbose_name_plural = "Task status"
	
