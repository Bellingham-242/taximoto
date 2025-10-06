from django.urls import path
from . import views
from .views import reservations_rapides_view, reservation_rapide_lu
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

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
    
    # Réservations
    path('reservation/<int:pk>/valider/', views.reservation_valider, name='reservation_valider'),
    path('reservation/<int:pk>/rejeter/', views.reservation_rejeter, name='reservation_rejeter'),
    path('reservation/<int:pk>/lu/', views.reservation_lu, name='reservation_lu'),

    # Abonnements
    path('abonnement/<int:pk>/valider/', views.abonnement_valider, name='abonnement_valider'),
    path('abonnement/<int:pk>/rejeter/', views.abonnement_rejeter, name='abonnement_rejeter'),
    path('abonnement/<int:pk>/lu/', views.abonnement_lu, name='abonnement_lu'),
    # Dashboard client
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('register/client/', views.register_client, name='register_client'),
    path('login/client/', views.client_login, name='client_login'),
    path('reservations/', views.reservation, name='reservation'),
    path('admin/clients/', views.clients_list, name='clients_list'),
    path('client/reservation/ajouter/', views.client_ajouter_reservation, name='client_ajouter_reservation'),
    path('client/abonnement/ajouter/', views.client_ajouter_abonnement, name='client_ajouter_abonnement'),
    path('reservation-rapide/', views.reservation_rapide_view, name='reservation_rapide'),
    path('reservations/', views.reservation, name='reservation'),
    path('reservation-lu/<int:pk>/', reservation_rapide_lu, name='reservation_rapide_lu'),
    path('admin/reservations-rapides/', views.reservations_admin, name='reservations_admin'),
    path('reservations-rapides/', views.liste_reservations_rapides, name='liste_reservations_rapides'),
    path('reservations-rapides/supprimer/<int:pk>/', views.supprimer_reservation, name='supprimer_reservation'),
    
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]
