from django.db import models
from social_auth.models import UserSocialAuth

class Pacchetti(models.Model):
	utente = models.ForeignKey(UserSocialAuth)
	data_acquisto = models.DateField()
	giorni = models.IntegerField()
	attivato = models.NullBooleanField(default = False)
	data_sottoscrizione = models.DateField(null = True, blank=True)
	data_scadenza = models.DateField(null = True, blank=True)

	class Meta:
		verbose_name = 'Pacchetto'
		verbose_name_plural = 'Pacchetti'

