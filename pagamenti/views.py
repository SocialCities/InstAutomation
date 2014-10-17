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


def estendi_scadenza(instance, giorni):
	pacchetto_obj = Pacchetti.objects.get(utente = instance, attivato = True)
	data_scadenza = pacchetto_obj.data_scadenza

	pacchetto_obj.data_scadenza = data_scadenza + timedelta(giorni)
	pacchetto_obj.save()


def percentuale_tempo_rimanente(instance):
	pacchetto_obj = Pacchetti.objects.get(utente = instance)

	now = date.today()
	data_scadenza = pacchetto_obj.data_scadenza

	delta_scadenza = data_scadenza - now  
	delta_scadenza = float(delta_scadenza.days)
	giorni_totali = float(pacchetto_obj.giorni)

	return 100-((delta_scadenza/giorni_totali)*100)


def get_dati_pacchetto(instance):
	pacchetto_obj = Pacchetti.objects.get(utente = instance)

	now = date.today()
	data_scadenza = pacchetto_obj.data_scadenza
	delta_scadenza = data_scadenza - now  
	delta_scadenza = delta_scadenza.days

	giorni_totali = pacchetto_obj.giorni

	return delta_scadenza, giorni_totali

