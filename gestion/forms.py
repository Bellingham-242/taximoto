from django import forms
from .models import Conducteur, Moto, Panne, Recette, Question

class AttributionMotoForm(forms.Form):
    conducteur = forms.ModelChoiceField(queryset=Conducteur.objects.all())
    moto = forms.ModelChoiceField(queryset=Moto.objects.filter(statut='disponible'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # S'assurer que le queryset du champ moto est toujours à jour
        self.fields['moto'].queryset = Moto.objects.filter(statut='disponible')

class PanneForm(forms.ModelForm):
    class Meta:
        model = Panne
        fields = ['moto', 'description', 'montant_depense']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Description des réparations'}),
            'montant_depense': forms.NumberInput(attrs={'placeholder': 'Montant dépensé'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On ne propose que les motos en réparation
        self.fields['moto'].queryset = Moto.objects.filter(statut='reparation')


class RecetteForm(forms.ModelForm):
    class Meta:
        model = Recette
        fields = ['conducteur', 'montant', 'depense']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # on récupère l'utilisateur connecté
        super().__init__(*args, **kwargs)

        if user.role == "conducteur":
            # On masque le champ conducteur car c'est lui-même
            self.fields['conducteur'].widget = forms.HiddenInput()
        else:
            # L'admin peut choisir parmi les conducteurs avec une moto attribuée
            self.fields['conducteur'].queryset = Conducteur.objects.filter(moto__isnull=False)


# Formulaire pour le visiteur
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['nom', 'email', 'sujet', 'message']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'}),
            'sujet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sujet'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre message', 'rows': 5}),
        }

# Formulaire pour que l'admin réponde
class ReponseForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['reponse']
        widgets = {
            'reponse': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Réponse de l’admin', 'rows': 5}),
        }