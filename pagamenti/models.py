from django.db import models
from social_auth.models import UserSocialAuth

class Abbonamenti(models.Model):
	utente = models.ForeignKey(UserSocialAuth)
	data_sottoscrizione = models.DateField(null = True)
	data_scadenza = models.DateField(null = True, blank = True)
	pagamento_ricorsivo = models.NullBooleanField()
			
	class Meta:
		verbose_name = "Abbonamenti"
		verbose_name_plural = "Abbonamento"
