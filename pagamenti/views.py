from .models import Pacchetti
from datetime import datetime, timedelta, date


def nuovo_pacchetto(instance, giorni):
	now = datetime.now()
	pacchetto_obj = Pacchetti(utente = instance, data_acquisto = now, giorni = giorni, attivato = False)
	pacchetto_obj.save()

def attiva_pacchetto(instance):
	esistenza_pacchetto_obj = Pacchetti.objects.filter(utente = instance, attivato = False).exists()
	if esistenza_pacchetto_obj:

		pacchetto_obj = Pacchetti.objects.get(utente = instance)
		giorni = pacchetto_obj.giorni

		now = datetime.now()
		scadenza = now + timedelta(giorni)

		pacchetto_obj.attivato = True
		pacchetto_obj.data_sottoscrizione = now
		pacchetto_obj.data_scadenza = scadenza
		pacchetto_obj.save()


def abbonamento_valido(instance):
	pacchetto_obj = Pacchetti.objects.get(utente = instance)
			
	now = date.today()
	data_scadenza = pacchetto_obj.data_scadenza

	if now > data_scadenza:
		return False #Abbonamento scaduto
	else:
		return True #Abbonamento valido