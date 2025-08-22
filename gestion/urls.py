from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('', views.touriste, name='touriste'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('recette/<int:recette_id>/modifier/', views.modifier_recette, name='modifier_recette'),
    path('conducteur/<int:conducteur_id>/modifier/', views.modifier_conducteur, name='modifier_conducteur'),
    path('attribuer-moto/', views.attribuer_moto, name='attribuer_moto'),
    path('ajouter-moto/', views.ajouter_moto, name='ajouter_moto'),
    path('supprimer-moto/<int:moto_id>/', views.supprimer_moto, name='supprimer_moto'),
    path('conducteur/<int:pk>/', views.conducteur_detail, name='conducteur_detail'),
    path("recettes/ajouter/", views.ajouter_recette, name="ajouter_recette"),
    path("conducteurs/", views.liste_conducteurs, name="liste_conducteurs"),
    path("conducteurs/supprimer/<int:pk>/", views.supprimer_conducteur, name="supprimer_conducteur"),
    path('poser-question/', views.poser_question, name='poser_question'),
    path('questions/', views.liste_questions, name='liste_questions'),
    path('questions/<int:question_id>/repondre/', views.repondre_question, name='repondre_question'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/conducteur/', views.conducteur_dashboard, name='conducteur_dashboard'),

    path('redirect/', views.home_redirect, name='redirect_by_role'),
    #routes ajoutes
    path('email',views.email, name='email'),
    path('modifier/<int:pk>/',views.modifier, name='modifier'),
    # path('paiement/<int:conducteur_id>/', views.ajouter_paiement, name='ajouter_paiement'),
    path('absence/<int:conducteur_id>/', views.ajouter_absence, name='ajouter_absence'),
    path('moto/<int:moto_id>/modifier_statut/', views.modifier_statut_moto, name='modifier_statut_moto'),
    path('bilan-general/', views.bilan_general, name='bilan_general'),
    path('pannes/ajouter/', views.ajouter_panne, name='ajouter_panne'),
    path('pannes/', views.liste_pannes, name='liste_pannes'),
]
