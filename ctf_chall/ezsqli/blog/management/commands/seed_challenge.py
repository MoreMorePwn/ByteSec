import os

from django.core.management.base import BaseCommand
from django.db import connection

from blog.models import AdminUser, Blog, QueryHelper


class Command(BaseCommand):
    help = "Seed the EzSQLi CTF challenge database."

    def handle(self, *args, **options):
        flag = os.environ.get("BYTESEC_EZSQLI_FLAG", "BYTESEC{196f5dee6f071643}")

        AdminUser.objects.all().delete()
        AdminUser.objects.create(username="admin", password="admin")

        Blog.objects.all().delete()
        Blog.objects.create(id=1, title="Welcome", content="The search endpoint accepts an id parameter.")
        Blog.objects.create(id=2, title="Debug", content="Debug helpers should never trust request parameters.")

        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS flag")
            cursor.execute("CREATE TABLE flag(flag TEXT)")
            cursor.execute("INSERT INTO flag(flag) VALUES (%s)", [flag])

        QueryHelper.debug_query = []
        self.stdout.write(self.style.SUCCESS("EzSQLi challenge seeded."))
