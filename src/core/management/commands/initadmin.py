from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.core.validators import validate_email
from django.core import exceptions
import logging
logging.getLogger().setLevel(logging.INFO)

class Command(BaseCommand):
    help = "Create an admin user"

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help="The username")
        parser.add_argument('email', type=str, help="The email")
        parser.add_argument('password', type=str, help="The password")

    def handle(self, *args, **options):
        try:
            username = options['username']
            email = options['email']
            password = options['password']
            try:
                validate_email(email)
            except exceptions.ValidationError as e:
                #raise CommandError('The email is not valid')
                logging.warn('The email is not valid')
            try:
                User.objects.create_superuser(username, email, password)
                logging.info(f'Created user {username}')
            except IntegrityError:
                #raise CommandError(f'An user with that username already exists')
                logging.warn(f'An user with that username already exists')
            except Exception as e:
                raise CommandError(f'{e}')
        except Exception as e:
            raise CommandError(str(e))