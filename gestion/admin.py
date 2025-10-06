from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Moto, Conducteur, Recette, Absence, Panne, Question, Client, Reservation, Abonnement, JourSemaine


# -----------------------
# Utilisateur avec rôle
# -----------------------

# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
#     list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
#     search_fields = ('username', 'role', 'email', 'first_name', 'last_name')
#     ordering = ('username',)

#     # Permet de modifier le rôle depuis la liste
#     list_editable = ('role',)

#     # Assure que le champ 'role' apparaisse dans le formulaire de modification
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email')}),
#         ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
#     )


# -----------------------
# Moto
# -----------------------
@admin.register(Moto)
class MotoAdmin(admin.ModelAdmin):
    list_display = ('nom', 'matricule', 'statut')
    list_filter = ('statut',)
    search_fields = ('nom', 'matricule')


# -----------------------
# Conducteur
# -----------------------
@admin.register(Conducteur)
class ConducteurAdmin(admin.ModelAdmin):
    list_display = ('user', 'telephone', 'adresse', 'moto')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'telephone')
    list_filter = ('moto__statut',)


# -----------------------
# Recette
# -----------------------
@admin.register(Recette)
class RecetteAdmin(admin.ModelAdmin):
    list_display = ('conducteur', 'date', 'jour', 'montant', 'depense', 'benefice')
    list_filter = ('jour', 'date')
    search_fields = ('conducteur__user__username',)
    date_hierarchy = 'date'


# -----------------------
# Absence
# -----------------------
@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ('conducteur', 'date', 'raison')
    list_filter = ('date',)
    search_fields = ('conducteur__user__username',)


# -----------------------
# Panne
# -----------------------
@admin.register(Panne)
class PanneAdmin(admin.ModelAdmin):
    list_display = ('moto', 'date', 'montant_depense', 'admin')
    list_filter = ('date', 'moto__statut')
    search_fields = ('moto__nom', 'moto__matricule')
    date_hierarchy = 'date'


# -----------------------
# Question
# -----------------------
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('sujet', 'nom', 'email', 'statut', 'date_creation', 'date_reponse')
    list_filter = ('statut', 'date_creation')
    search_fields = ('sujet', 'nom', 'email', 'message', 'reponse')
    date_hierarchy = 'date_creation'


# -----------------------
# Client
# -----------------------
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'whatsapp', 'adresse')
    search_fields = ('user__username', 'user__email', 'whatsapp', 'adresse')


# -----------------------
# Reservation
# -----------------------
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('client', 'date_course', 'heure_course', 'lieu_depart', 'lieu_arrivee', 'statut')
    list_filter = ('statut', 'date_course')
    search_fields = ('client__user__username', 'client__user__email', 'lieu_depart', 'lieu_arrivee')
    date_hierarchy = 'date_course'


# -----------------------
# Abonnement
# -----------------------
@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = ('client', 'heure_passage', 'lieu_depart', 'lieu_arrivee', 'statut', 'date_demande')
    list_filter = ('statut', 'date_demande')
    search_fields = ('client__user__username', 'client__user__email', 'lieu_depart', 'lieu_arrivee')
    filter_horizontal = ('jours',)
    date_hierarchy = 'date_demande'


# -----------------------
# JourSemaine
# -----------------------
@admin.register(JourSemaine)
class JourSemaineAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)
