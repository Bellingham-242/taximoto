from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Question  # si tu veux inclure les réservations publiées

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return ['touriste', 'client_login', 'register_client', 'reservation_rapide']

    def location(self, item):
        return reverse(item)

class ReservationSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return Question.objects.all()  # si tu veux lister toutes les réservations

    def lastmod(self, obj):
        return obj.date_created  # champ date de création
