from django.shortcuts import redirect
from functools import wraps
from .models import Conducteur

# Pour les conducteurs uniquement
def conducteur_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 🔒 Vérifie que l'utilisateur est connecté
        if not request.user.is_authenticated:
            return redirect('login')

        # 🔒 Vérifie le rôle
        if request.user.role != 'conducteur':
            return redirect('home')

        # 🔒 Vérifie qu’un objet Conducteur existe
        if not Conducteur.objects.filter(user=request.user).exists():
            return redirect('home')  # ou afficher un message

        return view_func(request, *args, **kwargs)
    return wrapper

# Pour les admins uniquement
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.role != 'admin':
            return redirect('home')

        return view_func(request, *args, **kwargs)
    return wrapper


# Pour les clients uniquement
def client_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 🔒 Vérifie que l'utilisateur est connecté
        if not request.user.is_authenticated:
            return redirect('login')

        # 🔒 Vérifie le rôle
        if request.user.role != 'client':
            return redirect('home')

        # 🔒 Vérifie qu’un objet Client existe
        if not hasattr(request.user, 'client'):
            return redirect('home')  # ou afficher un message

        return view_func(request, *args, **kwargs)
    return wrapper
