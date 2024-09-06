from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates a superuser'

    def handle(self, *args, **kwargs):
        username = 'shadik7'
        email = 'test@gmail.com'
        password = 'pass'

        user = User.objects.create_superuser(username=username, email=email, password=password)

        self.stdout.write(self.style.SUCCESS('\n' + '*' * 40))
        self.stdout.write(self.style.SUCCESS(' Superuser created successfully '))
        self.stdout.write(self.style.SUCCESS('*' * 40 + '\n'))
        self.stdout.write(self.style.SUCCESS(f' {self.style.HTTP_INFO("Username:")}   {username}'))
        self.stdout.write(self.style.SUCCESS(f' {self.style.HTTP_INFO("Email:")}      {email}'))
        self.stdout.write(self.style.SUCCESS(f' {self.style.HTTP_INFO("Password:")}   {password}\n'))
        self.stdout.write(self.style.SUCCESS('*' * 40 + '\n'))
