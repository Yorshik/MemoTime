# Generated by Django 4.2.16 on 2024-12-18 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("schedule", "0002_alter_event_description_alter_note_description_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="timeschedule",
            name="day_number",
            field=models.IntegerField(
                choices=[
                    (None, "Day"),
                    (1, "Monday"),
                    (2, "Tuesday"),
                    (3, "Wednesday"),
                    (4, "Thursday"),
                    (5, "Friday"),
                    (6, "Saturday"),
                    (7, "Sunday"),
                ],
                help_text="Day of the week (1-7)",
                verbose_name="day of the week",
            ),
        ),
    ]
