from django.core.management.base import BaseCommand

from commands.management.commands._update import UpdateLiveDB, UpdateHeroku


class Command(BaseCommand):
    update_local_heroku = UpdateLiveDB()
    update_heroku = UpdateHeroku()

    def add_arguments(self, parser):
        parser.add_argument(
            'process',
            nargs=1, type=str, choices=['local-heroku', 'heroku'],
            help='Specify whether to transfer filtered products to local live db (local-heroku) or to update heroku db from local live db'
        )

    def handle(self, *args, **options):
        process = options['process'][0]
        if process == 'heroku':
            self.update_heroku.execute()
        elif process == 'local-heroku':
            self.update_local_heroku.execute()

    
    