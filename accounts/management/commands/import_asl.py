import json
import csv
from django.core.management.base import BaseCommand
from accounts.models import SignWord

class Command(BaseCommand):
    help = 'Merges WLASL URLs with ASL-LEX Categories'

    def handle(self, *args, **kwargs):
        # 1. Load the Categories from the CSV
        category_map = {}
        csv_path = 'accounts/data/signdata.csv'
        with open(csv_path, mode='r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                category_map[row['EntryID'].lower()] = row['CDISemanticCategory']

        # 2. Load the URLs from the JSON
        json_path = 'accounts/data/WLASL_v0.3.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # --- FIX STARTS HERE ---
        # Ensure 'word_instances' starts at the same level as the 'with' blocks above
        word_instances = []
        for entry in data:
            word_text = entry['gloss']
            if entry.get('instances'):
                video_link = entry['instances'][0]['url']
                category_text = category_map.get(word_text.lower(), 'General')
                needs_bypass = 'haskins.yale.edu' in video_link or video_link.startswith('http://')

                # Append to list instead of saving to DB one by one
                word_instances.append(
                    SignWord(
                        word=word_text,
                        video_url=video_link,
                        category=category_text,
                        needs_ssl_bypass=needs_bypass
                    )
                )

        # 3. Wipe old data and do a BULK CREATE
        self.stdout.write("Deleting old entries...")
        SignWord.objects.all().delete()
        
        self.stdout.write("Uploading to Neon (this might take a few seconds)...")
        SignWord.objects.bulk_create(word_instances)

        self.stdout.write(self.style.SUCCESS(f'Successfully uploaded {len(word_instances)} signs!'))