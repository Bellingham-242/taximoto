from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from functools import wraps
from .models import Conducteur,ReservationRapide, Recette, Client, Moto, Absence, Question, Panne, Reservation, Abonnement
from django.db.models import Sum
from datetime import date
from django.utils.timezone import now
import calendar
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib.auth.hashers import make_password
from .forms import AttributionMotoForm, PanneForm, ReservationRapideForm, RecetteForm, QuestionForm, ReponseForm, ClientSignUpForm, ClientLoginForm, AbonnementForm, ReservationForm
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from .decorators import conducteur_required, admin_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
import random

User = get_user_model()

# Obtenir le jour de la semaine en français
def get_jour_francais():
    jour = calendar.day_name[now().weekday()]
    return {
        'Monday': 'Lundi',
        'Tuesday': 'Mardi',
        'Wednesday': 'Mercredi',
        'Thursday': 'Jeudi',
        'Friday': 'Vendredi',
        'Saturday': 'Samedi',
        'Sunday': 'Dimanche'
    }.get(jour, '')

# Redirection intelligente après login
@login_required
def home_redirect(request):
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'conducteur':
        return redirect('conducteur_dashboard')
    return redirect('home')

# Dashboard conducteur
@login_required
@conducteur_required
def conducteur_dashboard(request):
    conducteur = get_object_or_404(Conducteur, user=request.user)
    recette_du_jour = Recette.objects.filter(conducteur=conducteur, date=date.today()).first()

    if request.method == 'POST':
        montant = request.POST.get('montant') or 0
        depense = request.POST.get('depense') or 0
        Recette.objects.update_or_create(
            conducteur=conducteur,
            date=date.today(),
            defaults={
                'montant': montant,
                'depense': depense,
                'jour': get_jour_francais()
            }
        )
        return redirect('conducteur_dashboard')

    absences = Absence.objects.filter(conducteur=conducteur)

    return render(request, 'conducteur_dashboard.html', {
        'conducteur': conducteur,
        'recette_du_jour': recette_du_jour,
        'absences': absences
    })


# Dashboard admin
@login_required
@admin_required
def admin_dashboard(request):
    # ----------------------------
    # Conducteurs et recettes
    # ----------------------------
    conducteurs = Conducteur.objects.select_related('user', 'moto') \
        .annotate(total_recettes=Sum('recette__montant')) \
        .prefetch_related('recette_set')

    data_conducteurs = []
    for cond in conducteurs:
        recette_du_jour = next((r for r in cond.recette_set.all() if r.date == date.today()), None)
        data_conducteurs.append({
            'conducteur': cond,
            'recette_du_jour': recette_du_jour,
            'total_recettes': cond.total_recettes or 0,
        })

    # ----------------------------
    # Réservations et abonnements
    # ----------------------------
    reservations = Reservation.objects.all().order_by('-date_reservation')[:10]
    abonnements = Abonnement.objects.all().order_by('-date_demande')[:10]


    if request.user.role != "admin":
        return HttpResponseForbidden("Vous n'avez pas accès à cette page.")

    return render(request, 'admin_dashboard.html', {
        'conducteurs': data_conducteurs,
        'reservations': reservations,
        'abonnements': abonnements,
    })


# Absences - Admin uniquement
@login_required
@admin_required
def ajouter_absence(request, conducteur_id):
    conducteur = get_object_or_404(Conducteur, id=conducteur_id)
    if request.method == 'POST':
        date_absence = request.POST.get('date')
        raison = request.POST.get('raison')
        Absence.objects.create(
            conducteur=conducteur,
            date=date_absence,
            raison=raison
        )
        messages.success(request, f"Absence enregistrée pour {conducteur}.")
        return redirect('admin_dashboard')
    return render(request, 'ajouter_absence.html', {'conducteur': conducteur})

# Attribution moto avec statut
@login_required
@admin_required
def attribuer_moto(request):
    if request.method == "POST":
        form = AttributionMotoForm(request.POST)
        if form.is_valid():
            conducteur = form.cleaned_data['conducteur']
            moto = form.cleaned_data['moto']
            if Conducteur.objects.filter(moto=moto).exclude(id=conducteur.id).exists():
                messages.error(request, f"La moto {moto} est déjà attribuée à un autre conducteur.")
            else:
                conducteur.moto = moto
                conducteur.save()
                moto.statut = 'attribuee'
                moto.save()
                messages.success(request, f"La moto {moto} a été attribuée à {conducteur}.")
                return redirect('admin_dashboard')
    else:
        form = AttributionMotoForm()
    return render(request, 'attribuer_moto.html', {'form': form})

# Suppression moto => statut
@login_required
@admin_required
def supprimer_moto(request, moto_id):
    moto = get_object_or_404(Moto, id=moto_id)
    moto.statut = 'disponible'
    moto.save()
    moto.delete()
    messages.success(request, "Moto supprimée avec succès.")
    return redirect('ajouter_moto')


@login_required
@admin_required
def modifier_conducteur(request, conducteur_id):
    conducteur = get_object_or_404(Conducteur, id=conducteur_id)

    if request.method == 'POST':
        conducteur.user.username = request.POST.get('username')
        conducteur.user.email = request.POST.get('email')
        conducteur.telephone = request.POST.get('telephone')
        conducteur.adresse = request.POST.get('adresse')
        conducteur.user.save()
        conducteur.save()
        return redirect('admin_dashboard')

    return render(request, 'modifier_conducteur.html', {'conducteur': conducteur})


@login_required
@admin_required
def modifier_recette(request, recette_id):
    recette = get_object_or_404(Recette, id=recette_id)

    if request.method == 'POST':
        recette.montant = request.POST.get('montant')
        recette.depense = request.POST.get('depense')
        recette.save()
        return redirect('admin_dashboard')

    return render(request, 'modifier_recette.html', {'recette': recette})


def home(request):
    
    return render(request,'home.html')


def touriste(request):
    # Date actuelle
    today = timezone.now().date()
    
    # On calcule un "index de cycle" basé sur les jours, qui change tous les 2 jours
    cycle_index = (today.toordinal() // 2)

    # Récupérer toutes les questions répondue
    all_questions = list(Question.objects.filter(statut='repondu').order_by('-date_creation'))

    # Mélanger mais de façon stable avec le cycle (pour que tous les utilisateurs voient la même liste sur 2 jours)
    random.Random(cycle_index).shuffle(all_questions)

    # Limiter à 20 (ou le nombre que tu veux)
    questions = all_questions[:20]

    # Gestion du formulaire pour poser une question
    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        sujet = request.POST.get('sujet')
        message = request.POST.get('message')

        # Vérifier si l'utilisateur a déjà une question en attente
        if Question.objects.filter(email=email, statut='en_attente').exists():
            messages.warning(request, "Vous avez déjà une question en attente de réponse.")
        else:
            Question.objects.create(
                nom=nom,
                email=email,
                sujet=sujet,
                message=message
            )
            messages.success(request, "Votre question a été envoyée avec succès !")

    return render(request, 'touriste.html', {'questions': questions})



def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirige selon le rôle
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'conducteur':
                return redirect('conducteur_dashboard')

        else:
            messages.error(request, 'Nom ou mot de passe incorrect.')

    return render(request, 'login.html')

def custom_logout(request):
    logout(request)
    return redirect('home')  # redirige vers la page de home


def register(request):
    if Conducteur.objects.count() >= 100:
        messages.error(request, "Le nombre maximum de conducteurs (100) a été atteint.")
        return redirect('login')

    if request.method == 'POST':
        username = request.POST.get('username')
        email =request.POST.get('email')
        password = request.POST.get('password')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        telephone = request.POST.get('telephone')
        adresse = request.POST.get('adresse')  # ajoute ce champ dans le formulaire

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=prenom,
                last_name=nom,
                role='conducteur'
            )

            Conducteur.objects.create(
                user=user,
                telephone=telephone,
                adresse=adresse
            )

            messages.success(request, "Inscription réussie. Connectez-vous.")
            return redirect('login')

    return render(request, 'register.html')

@login_required
@admin_required
def ajouter_moto(request):
    motos = Moto.objects.all()

    if request.method == 'POST':
        if motos.count() >= 100:
            messages.error(request, "Nombre maximal de motos atteint (100).")
        else:
            nom = request.POST.get('nom')
            matricule = request.POST.get('matricule')

            if not nom or not matricule:
                messages.error(request, "Tous les champs sont requis.")
            elif Moto.objects.filter(matricule=matricule).exists():
                messages.error(request, "Ce matricule existe déjà.")
            else:
                Moto.objects.create(nom=nom, matricule=matricule)
                messages.success(request, "Moto ajoutée avec succès.")
                return redirect('ajouter_moto')

    return render(request, 'ajouter_moto.html', {'motos': motos})


@login_required
@admin_required
def conducteur_detail(request, pk):
    conducteur = get_object_or_404(Conducteur, pk=pk)
    recettes = Recette.objects.filter(conducteur=conducteur)

    total_montant = sum(recette.montant for recette in recettes)
    total_depense = sum(recette.depense for recette in recettes)
    net = total_montant - total_depense

    context = {
        'conducteur': conducteur,
        'moto': conducteur.moto,
        'total_montant': total_montant,
        'total_depense': total_depense,
        'net': net,
    }
    return render(request, 'conducteur_detail.html', context)


#les nouvelles vues
def email(request): 
    if request.method == "POST":
        data=request.POST
        email=data.get("email")
        user=User.objects.filter(email=email).last()
        if user:
            print("l'email est bien correct")
            return redirect("modifier", user.id)
        else:
            print("l'email est incorrect")
            return redirect("email")
    return render(request, 'email.html') 

def modifier(request,pk): 
    if request.method == "POST":
        data=request.POST
        if data.get("password")==data.get("confirm_password"):
            user=User.objects.get(id=int(pk))
            user.set_password(data.get("password"))
            user.save()
            return redirect("home")
        else:
            return redirect("modifier",user.id)   
    return render(request, 'modifier.html') 


def modifier_statut_moto(request, moto_id):
    moto = get_object_or_404(Moto, id=moto_id)

    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        if nouveau_statut in ['disponible', 'attribuee', 'reparation']:
            moto.statut = nouveau_statut
            moto.save()
            messages.success(request, f"Le statut de la moto '{moto.nom}' a été mis à jour.")
        else:
            messages.error(request, "Statut invalide.")

    # redirige vers la page actuelle (ou tableau de bord)
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))


def bilan_general(request):
    # Recettes et dépenses (depuis Recette)
    total_recettes = Recette.objects.aggregate(total=Sum('montant'))['total'] or 0
    total_depenses = Recette.objects.aggregate(total=Sum('depense'))['total'] or 0

    # Dépenses liées aux pannes
    total_pannes = Panne.objects.aggregate(total=Sum('montant_depense'))['total'] or 0

    # Bénéfice net = recettes - (dépenses + pannes)
    benefice_total = total_recettes - (total_depenses + total_pannes)

    # Statistiques diverses
    nb_conducteurs = Conducteur.objects.count()
    nb_motos_disponibles = Moto.objects.filter(statut='disponible').count()
    nb_motos_attribuees = Moto.objects.filter(statut='attribuee').count()
    nb_motos_reparation = Moto.objects.filter(statut='reparation').count()

    context = {
        'total_recettes': total_recettes,
        'total_depenses': total_depenses,
        'total_pannes': total_pannes,
        'benefice_total': benefice_total,
        'nb_conducteurs': nb_conducteurs,
        'nb_motos_disponibles': nb_motos_disponibles,
        'nb_motos_attribuees': nb_motos_attribuees,
        'nb_motos_reparation': nb_motos_reparation,
    }

    return render(request, 'bilan_general.html', context)

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'admin':
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@user_passes_test(admin_required)
def ajouter_panne(request):
    if request.method == "POST":
        form = PanneForm(request.POST, request.FILES)
        if form.is_valid():
            panne = form.save(commit=False)
            panne.admin = request.user
            panne.save()
            return redirect('liste_pannes')
    else:
        form = PanneForm()
    return render(request, 'pannes/ajouter_panne.html', {'form': form})

@login_required
@user_passes_test(admin_required)
def liste_pannes(request):
    from .models import Panne
    pannes = Panne.objects.select_related('moto', 'admin').all()
    return render(request, 'pannes/liste_pannes.html', {'pannes': pannes})

@login_required
def ajouter_recette(request):
    if request.method == "POST":
        form = RecetteForm(request.POST, user=request.user)
        if form.is_valid():
            recette = form.save(commit=False)

            # Attribution automatique du conducteur si rôle "conducteur"
            if request.user.role == "conducteur":
                recette.conducteur = Conducteur.objects.get(user=request.user)

            # Vérification si une recette existe déjà pour ce conducteur et cette date
            if Recette.objects.filter(conducteur=recette.conducteur, date=recette.date).exists():
                messages.error(request, "Une recette pour ce conducteur à cette date existe déjà !")
            else:
                recette.save()
                messages.success(request, "Recette ajoutée avec succès !")
                return redirect('admin_dashboard')  # ou ta page cible

    else:
        form = RecetteForm(user=request.user)

    return render(request, "recettes/ajouter.html", {"form": form})


@login_required
def liste_conducteurs(request):
    if request.user.role != "admin":
        messages.error(request, "Accès refusé")
        return redirect("dashboard")  # redirige si pas admin

    conducteurs = Conducteur.objects.all()
    return render(request, "conducteurs/liste.html", {"conducteurs": conducteurs})


@login_required
def supprimer_conducteur(request, pk):
    if request.user.role != "admin":
        messages.error(request, "Accès refusé")
        return redirect("dashboard")

    conducteur = get_object_or_404(Conducteur, pk=pk)

    if request.method == "POST":
        conducteur.delete()
        messages.success(request, f"Le conducteur {conducteur.user.get_full_name()} a été supprimé.")
        return redirect("liste_conducteurs")

    return render(request, "conducteurs/confirmer_suppression.html", {"conducteur": conducteur})



# 1. Page d'accueil ou section pour poser une question
def poser_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        # Vérifier si le visiteur n'a pas déjà une question en attente
        email = request.POST.get('email')
        if Question.objects.filter(email=email, statut='en_attente').exists():
            messages.error(request, "Vous avez déjà une question en attente de réponse.")
        elif form.is_valid():
            form.save()
            messages.success(request, "Votre question a été envoyée. L'administrateur vous répondra bientôt.")
            return redirect('poser_question')
    else:
        form = QuestionForm()
    return render(request, 'poser_question.html', {'form': form})

# 2. Dashboard admin - lister les questions
@login_required
def liste_questions(request):
    if not request.user.role == 'admin':
        messages.error(request, "Accès refusé.")
        return redirect('home')
    questions = Question.objects.all().order_by('-date_creation')  # ordre décroissant
    return render(request, 'liste_questions.html', {'questions': questions})

# 3. Répondre à une question
@login_required
def repondre_question(request, question_id):
    if not request.user.role == 'admin':
        messages.error(request, "Accès refusé.")
        return redirect('home')
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        form = ReponseForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.statut = 'repondu'
            question.date_reponse = timezone.now()
            question.save()
            messages.success(request, "Réponse envoyée avec succès.")
            return redirect('liste_questions')
    else:
        form = ReponseForm(instance=question)
    return render(request, 'repondre_question.html', {'form': form, 'question': question})


# -----------------------------
# GESTION DES RÉSERVATIONS
# -----------------------------
@login_required
@admin_required
def reservation_valider(request, pk):
    res = get_object_or_404(Reservation, pk=pk)
    res.statut = 'valide'
    res.save()
    messages.success(request, f"La réservation de {res.client.user.username} a été validée.")
    return redirect('admin_dashboard')

@login_required
@admin_required
def reservation_rejeter(request, pk):
    res = get_object_or_404(Reservation, pk=pk)
    res.statut = 'rejete'
    res.save()
    messages.warning(request, f"La réservation de {res.client.user.username} a été rejetée.")
    return redirect('admin_dashboard')

@login_required
@admin_required
def reservation_lu(request, pk):
    res = get_object_or_404(Reservation, pk=pk)
    res.statut = 'lu'
    res.save()
    messages.info(request, f"La réservation de {res.client.user.username} a été marquée comme lue.")
    return redirect('admin_dashboard')


# -----------------------------
# GESTION DES ABONNEMENTS
# -----------------------------
@login_required
@admin_required
def abonnement_valider(request, pk):
    ab = get_object_or_404(Abonnement, pk=pk)
    ab.statut = 'valide'
    ab.save()
    messages.success(request, f"L'abonnement de {ab.client.user.username} a été validé.")
    return redirect('admin_dashboard')

@login_required
@admin_required
def abonnement_rejeter(request, pk):
    ab = get_object_or_404(Abonnement, pk=pk)
    ab.statut = 'rejete'
    ab.save()
    messages.warning(request, f"L'abonnement de {ab.client.user.username} a été rejeté.")
    return redirect('admin_dashboard')

@login_required
@admin_required
def abonnement_lu(request, pk):
    ab = get_object_or_404(Abonnement, pk=pk)
    ab.statut = 'lu'
    ab.save()
    messages.info(request, f"L'abonnement de {ab.client.user.username} a été marqué comme lu.")
    return redirect('admin_dashboard')

@login_required
def client_dashboard(request):
    # Récupère uniquement les réservations du client
    reservations = Reservation.objects.filter(client__user=request.user).order_by('-date_reservation')

    # Récupère uniquement les abonnements du client
    abonnements = Abonnement.objects.filter(client__user=request.user).order_by('-date_demande')

    return render(request, 'client_dashboard.html', {
        'reservations': reservations,
        'abonnements': abonnements,
    })


def register_client(request):
    if request.method == 'POST':
        form = ClientSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre compte client a été créé avec succès ! Vous pouvez maintenant vous connecter.")
            return redirect('client_login')
    else:
        form = ClientSignUpForm()
    return render(request, 'register_client.html', {'form': form})

def client_login(request):
    if request.method == 'POST':
        form = ClientLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} !")
            return redirect('client_dashboard')  # redirige vers le dashboard client
    else:
        form = ClientLoginForm()
    return render(request, 'client_login.html', {'form': form})

    
@login_required
@admin_required
def reservation(request):
    reservations = Reservation.objects.select_related('client__user').order_by('-date_reservation')
    abonnements = Abonnement.objects.select_related('client__user').prefetch_related('jours').order_by('-date_demande')

    # Totaux pour les réservations
    total_res_valide = reservations.filter(statut='valide').count()
    total_res_attente = reservations.filter(statut='en_attente').count()
    total_res_rejete = reservations.filter(statut='rejete').count()

    # Totaux pour les abonnements
    total_ab_valide = abonnements.filter(statut='valide').count()
    total_ab_attente = abonnements.filter(statut='en_attente').count()
    total_ab_rejete = abonnements.filter(statut='rejete').count()

    context = {
        'reservations': reservations,
        'abonnements': abonnements,
        'res_totals': {
            'valide': total_res_valide,
            'attente': total_res_attente,
            'rejete': total_res_rejete,
        },
        'ab_totals': {
            'valide': total_ab_valide,
            'attente': total_ab_attente,
            'rejete': total_ab_rejete,
        }
    }

    return render(request, 'reservation.html', context)


    
@login_required
@admin_required
def clients_list(request):
    clients = Client.objects.select_related('user').all()
    return render(request, 'clients_list.html', {'clients': clients})

@login_required
def client_ajouter_reservation(request):
    if request.user.role != 'client':
        return HttpResponseForbidden("Vous n'avez pas accès à cette page.")

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            res = form.save(commit=False)
            res.client = request.user.client
            res.save()
            messages.success(request, "Votre réservation a été enregistrée !")
            return redirect('client_dashboard')
    else:
        form = ReservationForm()

    return render(request, 'client_form_reservation.html', {'form': form})

@login_required
def client_ajouter_abonnement(request):
    if request.user.role != 'client':
        return HttpResponseForbidden("Vous n'avez pas accès à cette page.")

    if request.method == 'POST':
        form = AbonnementForm(request.POST)
        if form.is_valid():
            ab = form.save(commit=False)
            ab.client = request.user.client
            ab.save()
            form.save_m2m()  # pour enregistrer les jours sélectionnés
            messages.success(request, "Votre abonnement a été enregistré !")
            return redirect('client_dashboard')
    else:
        form = AbonnementForm()

    return render(request, 'client_form_abonnement.html', {'form': form})



def reservations_rapides_view(request):
    reservations_rapides = ReservationRapide.objects.all().order_by('-date_creation')
    return render(request, 'reservations_rapides.html', {'reservations_rapides': reservations_rapides})

def reservation_rapide_lu(request, pk):
    rr = get_object_or_404(ReservationRapide, pk=pk)
    rr.statut = 'lu'
    rr.save()
    return redirect('reservations_rapides')



def reservation_rapide_view(request):
    """
    Vue pour permettre aux utilisateurs d'envoyer une réservation rapide.
    """
    if request.method == 'POST':
        form = ReservationRapideForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            
            # Si l'utilisateur est connecté, on lie automatiquement son profil client
            if request.user.is_authenticated and hasattr(request.user, 'client'):
                reservation.client = request.user.client
            
            reservation.save()
            messages.success(request, "Votre réservation rapide a été envoyée avec succès !")
            return redirect('reservation_rapide')  # nom de l’URL à adapter
    else:
        form = ReservationRapideForm()

    context = {
        'form': form
    }
    return render(request, 'reservation_rapide.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def reservations_admin(request):
    reservations = ReservationRapide.objects.select_related('client').order_by('-date_creation')
    return render(request, 'reservations_admin.html', {'reservations': reservations})

@login_required
@staff_member_required  # si seulement les admins peuvent voir
def liste_reservations_rapides(request):
    reservations = ReservationRapide.objects.select_related('client').order_by('-date_creation')
    context = {
        'reservations': reservations
    }
    return render(request, 'liste_reservations_rapides.html', context)

@login_required
@staff_member_required  # seulement admin
def supprimer_reservation(request, pk):
    reservation = get_object_or_404(ReservationRapide, pk=pk)
    reservation.delete()
    messages.success(request, "La réservation a été supprimée avec succès.")
    return redirect('liste_reservations_rapides')