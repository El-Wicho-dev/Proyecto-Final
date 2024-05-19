from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
import os

class Command(BaseCommand):
    help = 'Deletes all files in the /media/temp directory'

    def handle(self, *args, **options):
        temp_dir = 'media/temp'
        for filename in default_storage.listdir(temp_dir)[1]:  # [1] para obtener archivos, [0] para directorios
            file_path = os.path.join(temp_dir, filename)
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                self.stdout.write(self.style.SUCCESS(f'Successfully deleted {filename}'))
            else:
                self.stdout.write(self.style.WARNING(f'File {filename} already deleted'))
