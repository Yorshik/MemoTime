# Generated by Django 4.2.16 on 2024-12-11 18:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("feedback", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="personaldata",
            old_name="mail",
            new_name="email",
        ),
    ]
