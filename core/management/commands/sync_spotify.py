import os
import time
import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from tqdm import tqdm
from core.services.spotify import SpotifyService
from core.models import Artist, ArtistAlias

class Command(BaseCommand):
    help = "Sync one or more artists from Spotify into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            '--artist',
            action='append',
            help='Name of the artist to import. Can be used multiple times.',
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Path to a file containing one artist name per line',
        )
        parser.add_argument(
            '--sleep',
            type=float,
            default=1,
            help='Sleep time (in seconds) between requests to avoid rate limiting',
        )

    def handle(self, *args, **options):
        service = SpotifyService()
        artists_to_process = []

        if options['artist']:
            artists_to_process.extend(options['artist'])

        if options['file']:
            try:
                with open(options['file'], 'r') as f:
                    artists_to_process.extend([line.strip() for line in f if line.strip()])
            except FileNotFoundError:
                self.stderr.write(self.style.ERROR(f"File not found: {options['file']}"))
                return

        if not artists_to_process:
            self.stderr.write(self.style.ERROR("No artists provided. Use --artist or --file."))
            return
        
        log_dir = os.path.join("data", "logs")
        os.makedirs(log_dir, exist_ok=True) 

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = os.path.join(log_dir, f"spotify_sync_log_{timestamp}.txt")
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
        )

        six_months_ago = timezone.now() - timedelta(days=180)
        total = len(artists_to_process)

        self.stdout.write(self.style.NOTICE(f"🎧 Syncing {total} artist(s)...\n"))
        logging.info(f"Starting sync for {total} artists")

        for name in tqdm(artists_to_process, desc="Syncing artists", ncols=80):
            # Check if artist already synced recently
            match = Artist.objects.filter(name__iexact=name).first()
            if match and match.last_synced_at and match.last_synced_at > six_months_ago:
                msg = f"⏭️ Skipping recently-synced artist: {name}"
                self.stdout.write(self.style.WARNING(msg))
                logging.info(msg)
                continue

            alias_match = ArtistAlias.objects.filter(name_used__iexact=name).select_related('artist').first()
            if alias_match:
                artist = alias_match.artist
                if artist.last_synced_at and artist.last_synced_at > six_months_ago:
                    msg = f"⏭️ Skipping alias (recently synced): {name} → {artist.name}"
                    self.stdout.write(self.style.WARNING(msg))
                    logging.info(msg)
                    continue

            self.stdout.write(self.style.NOTICE(f"🔍 Searching for: {name}"))
            logging.info(f"Searching: {name}")

            try:
                spotify_artist = service.search_artist(name)
                if not spotify_artist:
                    msg = f"❌ Artist not found: {name}"
                    self.stderr.write(self.style.WARNING(msg))
                    logging.warning(msg)
                    continue

                artist_obj = service.save_artist_and_albums(spotify_artist, imported_as=name)
                msg = f"✅ Synced: {artist_obj.name}"
                self.stdout.write(self.style.SUCCESS(msg))
                logging.info(msg)

            except Exception as e:
                # Gracefully handle Spotify API errors like timeouts
                msg = f"⚠️ Error syncing {name}: {str(e)}"
                self.stderr.write(self.style.ERROR(msg))
                logging.error(msg)
                continue


            time.sleep(options['sleep'])

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Sync complete. Log written to: {log_filename}"))
        logging.info("Sync complete.")
