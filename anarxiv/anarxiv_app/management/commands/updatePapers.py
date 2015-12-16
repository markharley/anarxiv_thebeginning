from django.core.management.base import BaseCommand, CommandError
from anarxiv_app.views import updatePapers

class Command(BaseCommand):
    help = 'Rips the new daily papers from the RSS feed'

    def handle(self, *args, **options):
        updatePapers()
      