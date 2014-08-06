from django import forms

from .models import UtentiRivali

class CercaCompetitorForm(forms.ModelForm):
	
	class Meta:
		model = UtentiRivali
		fields = ("username",)


class RivaliForm(forms.ModelForm):
	
	class Meta:
		model = UtentiRivali
		fields = ("username", 'id_utente')
