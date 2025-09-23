from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Conducteur, Recette, Moto, Absence, Question, Panne
from django.db.models import Sum
from datetime import date
from django.utils.timezone import now
import calendar
from .forms import AttributionMotoForm, PanneForm, RecetteForm, QuestionForm, ReponseForm
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
    conducteurs = Conducteur.objects.select_related('user', 'moto') \
        .annotate(total_recettes=Sum('recette__montant')) \
        .prefetch_related('recette_set')

    data = []
    for cond in conducteurs:
        recette_du_jour = next((r for r in cond.recette_set.all() if r.date == date.today()), None)
        data.append({
            'conducteur': cond,
            'recette_du_jour': recette_du_jour,
            'total_recettes': cond.total_recettes or 0,
        })
        
    if request.user.role != "admin":
        return HttpResponseForbidden("Vous n'avez pas accès à cette page.")

    return render(request, 'admin_dashboard.html', {'conducteurs': data})

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

def admin_required(user):
    return user.is_authenticated and user.role == 'admin'

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
