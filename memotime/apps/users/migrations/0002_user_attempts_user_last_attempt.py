# Generated by Django 4.2.16 on 2024-12-12 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="attempts",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="last_attempt",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
