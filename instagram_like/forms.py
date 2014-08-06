from django import forms

from .models import ListaTag

class TagForm(forms.ModelForm):
	
	class Meta:
		model = ListaTag
		fields = ("keyword",)
