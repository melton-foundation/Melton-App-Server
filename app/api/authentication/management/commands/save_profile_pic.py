import json
from pathlib import Path

from authentication import services
from authentication.models import AppUser, Profile
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    A django management command to upload or change the profile pictures of users
    It can upload image files or use the URLs to change in database

    Inheritance:
        BaseCommand:

    """
    help = "Save profile pictures. Give a mapping file of email to image path or relative URL. To use URLs, use flag --url"

    def add_arguments(self, parser):
        parser.add_argument("file", metavar="mapping_file", type=str,
                            help="Path to file mapping email to picture files or urls")
        parser.add_argument("--url", action="store_true",
                            help="Use urls directly to save into database")

    def handle(self, *args, **options):
        mapping_file = Path(options.get("file"))
        if not mapping_file.exists():
            self.stderr.write(f"ERROR: File {mapping_file} not found")
            return

        with mapping_file.open() as file:
            try:
                mapping = json.load(file)
            except json.decoder.JSONDecodeError:
                self.stderr.write(
                    f"ERROR: File {mapping_file} is not a valid json file.")
                return

        if options.get("url"):
            self.handle_url_save(mapping)
        else:
            self.handle_file_save(mapping)

    def get_profile(self, email):
        profile = None
        try:
            profile = services.get_profile(email=email)
        except (AppUser.DoesNotExist, Profile.DoesNotExist):
            self.stderr.write(
                f"ERROR: Email {email} does not exist in database. Continuing...")
        return profile

    def handle_file_save(self, mapping):
        count = 0
        for email, path in mapping.items():
            image_file = Path(path)
            if not image_file.exists():
                self.stderr.write(
                    f"ERROR: File {image_file} does not exist. Continuing...")
                continue
            try:
                with image_file.open(mode='rb') as file:
                    services.save_profile_picture(
                        File(file), image_file.suffix, email=email)
                count += 1
            except (AppUser.DoesNotExist, Profile.DoesNotExist):
                self.stderr.write(
                    f"ERROR: Email {email} does not exist in database. Continuing...")

        self.stdout.write(
            f"SUCCESS: {count} Profile pictures have been stored")

    def handle_url_save(self, mapping):
        count = 0
        for email, url in mapping.items():
            profile = self.get_profile(email)
            if profile is None:
                continue

            if not url.startswith(profile.picture.field.upload_to):
                self.stderr.write(
                    f"ERROR: URL {url} is not relative to storage folder of Profile pictures. Continuing...")
                continue
            profile.picture = url
            profile.save()
            count += 1

        self.stdout.write(
            f"SUCCESS: {count} Profile pictures have been stored")
