from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Moto, Conducteur, Recette, Absence, Panne, Question


# -----------------------
# Utilisateur avec rôle
# -----------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


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
