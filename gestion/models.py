from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_migrate
from django.dispatch import receiver


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
    ('Dimanche', 'Dimanche'),
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





# =========================
#  CLIENT
# =========================
class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client")
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.whatsapp})"


# =========================
#  RESERVATION
# =========================
class Reservation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('lu', 'Lu par client'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="reservations")
    date_reservation = models.DateTimeField(auto_now_add=True)
    date_course = models.DateField()
    heure_course = models.TimeField()
    lieu_depart = models.CharField(max_length=255)
    lieu_arrivee = models.CharField(max_length=255)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    def __str__(self):
        return f"Réservation de {self.client.user.username} le {self.date_course} ({self.statut})"


# =========================
#  ABONNEMENT
# =========================
class Abonnement(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('lu', 'Lu par client'),
    ]

    JOURS_CHOICES = [
        ('lundi', 'Lundi'),
        ('mardi', 'Mardi'),
        ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'),
        ('vendredi', 'Vendredi'),
        ('samedi', 'Samedi'),
        ('dimanche', 'Dimanche'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="abonnements")
    jours = models.ManyToManyField("JourSemaine", blank=True)  # jours choisis
    heure_passage = models.TimeField()
    lieu_depart = models.CharField(max_length=255)
    lieu_arrivee = models.CharField(max_length=255)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_demande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Abonnement de {self.client.user.username} ({self.statut})"


# =========================
#  JOURS DE LA SEMAINE
# =========================
class JourSemaine(models.Model):
    nom = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nom

@receiver(post_migrate)
def create_jours_semaine(sender, **kwargs):
    from .models import JourSemaine  # éviter import circulaire
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    for jour in jours:
        JourSemaine.objects.get_or_create(nom=jour)
        
class ReservationRapide(models.Model):
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nom = models.CharField(max_length=150, blank=True, null=True)
    lieu = models.CharField(max_length=200, blank=True, null=True)
    destination = models.CharField(max_length=200, blank=True, null=True)
    heure = models.TimeField(blank=True, null=True)
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    statut = models.CharField(max_length=20, default='en attente')  # 'en attente' ou 'lu'
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom or (self.client.username if self.client else 'Anonyme')} - {self.sujet}"
