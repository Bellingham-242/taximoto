from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

# -----------------------
# Utilisateur avec rôle
# -----------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrateur'),
        ('conducteur', 'Conducteur'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='conducteur')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# -----------------------
# Moto
# -----------------------
class Moto(models.Model):
    STATUT_CHOICES = (
        ('disponible', 'Disponible'),
        ('attribuee', 'Attribuée'),
        ('reparation', 'En réparation'),
    )
    nom = models.CharField(max_length=100)
    matricule = models.CharField(max_length=50, unique=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='disponible')

    def __str__(self):
        return f"{self.nom} - {self.matricule} ({self.get_statut_display()})"


# -----------------------
# Conducteur
# -----------------------
class Conducteur(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)
    moto = models.OneToOneField(Moto, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# -----------------------
# Jours de la semaine
# -----------------------
JOURS_SEMAINE = [
    ('Lundi', 'Lundi'),
    ('Mardi', 'Mardi'),
    ('Mercredi', 'Mercredi'),
    ('Jeudi', 'Jeudi'),
    ('Vendredi', 'Vendredi'),
    ('Samedi', 'Samedi'),
]


# -----------------------
# Recette
# -----------------------
class Recette(models.Model):
    conducteur = models.ForeignKey(Conducteur, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    jour = models.CharField(max_length=10, choices=JOURS_SEMAINE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    depense = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('conducteur', 'date')
        ordering = ['-date']

    @property
    def benefice(self):
        """Calcul automatique du bénéfice net"""
        return self.montant - self.depense

    def __str__(self):
        return f"{self.conducteur} - {self.date} : {self.montant} FCFA"


# -----------------------
# Absences
# -----------------------
class Absence(models.Model):
    conducteur = models.ForeignKey(Conducteur, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    raison = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.conducteur} absent le {self.date}"


# -----------------------
# Panne pour moto en réparation
# -----------------------
class Panne(models.Model):
    moto = models.ForeignKey(Moto, on_delete=models.CASCADE, related_name='pannes')
    date = models.DateField(default=timezone.now)
    description = models.TextField(help_text="Description des réparations ou matériels achetés")
    montant_depense = models.DecimalField(max_digits=10, decimal_places=2, help_text="Montant total dépensé")
    facture = models.FileField(upload_to='factures/', null=True, blank=True, help_text="Ajouter un fichier de facture si disponible")
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'admin'}, help_text="Administrateur ayant enregistré la panne")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Panne de {self.moto.nom} le {self.date} - Dépense : {self.montant_depense} FCFA"


# -----------------------
# Questions des utilisateurs
# -----------------------
class Question(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente de réponse'),
        ('repondu', 'Répondu'),
    ]
    
    nom = models.CharField(max_length=255)  # nom du visiteur
    email = models.EmailField()             # email pour réponse
    sujet = models.CharField(max_length=255)
    message = models.TextField()
    reponse = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_reponse = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.sujet} - {self.nom}"

