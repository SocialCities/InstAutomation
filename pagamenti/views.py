from django.shortcuts import render
from .models import Abbonamenti
from datetime import datetime, timedelta, date

def crea_abbonamento_n_giorni(instance, giorni):
	now = datetime.now()
	scadenza = now + timedelta(giorni)
	nuovo_abbonamento = Abbonamenti(utente = instance, data_sottoscrizione = now, data_scadenza = scadenza, pagamento_ricorsivo = False)
	nuovo_abbonamento.save()
