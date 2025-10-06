from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Conducteur, Moto, Panne, Recette, Question, Reservation, Abonnement, JourSemaine, ReservationRapide
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()

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
        

class ClientLoginForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Votre nom d’utilisateur'
    }))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Votre mot de passe'
    }))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Nom d'utilisateur ou mot de passe incorrect.")
            if user.role != 'client':
                raise forms.ValidationError("Ce compte n'est pas un client.")
            cleaned_data['user'] = user
        return cleaned_data



class ClientSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    whatsapp = forms.CharField(max_length=20, required=True, help_text="Numéro WhatsApp")
    adresse = forms.CharField(max_length=200, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'whatsapp', 'adresse', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'client'  # On définit le rôle comme client
        if commit:
            user.save()
            # Crée automatiquement l'objet Client lié
            from .models import Client
            Client.objects.create(
                user=user,
                whatsapp=self.cleaned_data['whatsapp'],
                adresse=self.cleaned_data['adresse']
            )
        return user


# -------------------------------
# Formulaire pour Réservation
# -------------------------------
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date_course', 'heure_course', 'lieu_depart', 'lieu_arrivee']
        widgets = {
            'date_course': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'heure_course': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'lieu_depart': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu de départ'}),
            'lieu_arrivee': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu d’arrivée'}),
        }


# -------------------------------
# Formulaire pour Abonnement
# -------------------------------
class AbonnementForm(forms.ModelForm):
    jours = forms.ModelMultipleChoiceField(
        queryset=JourSemaine.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Abonnement
        fields = ['jours', 'heure_passage', 'lieu_depart', 'lieu_arrivee']
        widgets = {
            'heure_passage': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'lieu_depart': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu de départ'}),
            'lieu_arrivee': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu d’arrivée'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On charge les jours de semaine disponibles
        self.fields['jours'].queryset = JourSemaine.objects.all()
        
 


class ReservationRapideForm(forms.ModelForm):
    class Meta:
        model = ReservationRapide
        fields = ['client', 'sujet','whatsapp', 'message']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro WhatsApp:+242XXXXXXXXX'}),
            'sujet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sujet'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre message', 'rows': 4}),
        }