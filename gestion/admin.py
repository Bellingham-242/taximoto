from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .models import Moto, Conducteur,Recette


class UserAdmin(BaseUserAdmin):
    # Affiche le champ "role" dans l'admin
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Rôle', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')

# admin.site.register(User, UserAdmin)
admin.site.register(Moto)
admin.site.register(Conducteur)
admin.site.register(Recette)