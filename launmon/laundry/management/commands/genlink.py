from django.core.management.base import BaseCommand, CommandError
from laundry.models import User
from sesame.utils import get_query_string

class Command(BaseCommand):
    help = "Generate the magic link for a site"

    def add_arguments(self, parser):
        parser.add_argument("user", type=str)

    def handle(self, *args, **options):
        user = User.objects.get(username=options["user"])
        s = get_query_string(user)

        self.stdout.write(
            self.style.SUCCESS('Here is your magic link arg: %s' % s)
        )
        print(s)

