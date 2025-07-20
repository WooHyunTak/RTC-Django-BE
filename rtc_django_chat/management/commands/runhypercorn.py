import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run ASGI server (Hypercorn)"

    def add_arguments(self, parser):
        parser.add_argument("-p", "--port", type=int, default=18030)
        parser.add_argument("--host", type=str, default="127.0.0.1")

    def handle(self, *args, **options):
        self.stdout.write("Starting Hypercorn ASGI server...")
        port = options["port"]
        host = options["host"]
        try:
            subprocess.call(
                [
                    "python",
                    "-m",
                    "hypercorn",
                    "rtc_django_chat.asgi:application",
                    "--bind",
                    f"{host}:{port}",
                    "--workers",
                    "1",
                ]
            )
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("\nServer stopped"))
