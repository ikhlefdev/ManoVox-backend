import json
import csv
from django.core.management.base import BaseCommand
from accounts.models import SignWord

class Command(BaseCommand):
    help = 'Merges WLASL URLs with ASL-LEX Categories'

    def handle(self, *args, **kwargs):
        # 1. Load the Categories from the CSV into a Python Dictionary for fast lookup
        category_map = {}
        csv_path = 'accounts/data/signdata.csv'
        with open(csv_path, mode='r', encoding='latin-1') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Store it as: {'tree': 'Outside Things', 'apple': 'Food'}
                category_map[row['EntryID'].lower()] = row['CDISemanticCategory']

        # 2. Load the URLs from your original JSON
        json_path = 'accounts/data/WLASL_v0.3.json' # Make sure this path is correct!
        with open(json_path, 'r') as f:
            data = json.load(f)

        count = 0
        for entry in data:
            word_text = entry['gloss']
            if entry['instances']:
                video_link = entry['instances'][0]['url']
                
                # Look up the category from our map, default to 'General' if not found
                category_text = category_map.get(word_text.lower(), 'General') 

                # Check for SSL issues
                needs_bypass = 'haskins.yale.edu' in video_link or video_link.startswith('http://')

                SignWord.objects.update_or_create(
                    word=word_text,
                    defaults={
                        'video_url': video_link,
                        'category': category_text,
                        'needs_ssl_bypass': needs_bypass
                    }
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully merged {count} signs with categories!'))