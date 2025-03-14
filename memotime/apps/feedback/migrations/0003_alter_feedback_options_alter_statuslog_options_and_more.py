# Generated by Django 4.2.16 on 2024-12-12 18:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("feedback", "0002_rename_mail_personaldata_email"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="feedback",
            options={"verbose_name": "feedback", "verbose_name_plural": "feedbacks"},
        ),
        migrations.AlterModelOptions(
            name="statuslog",
            options={
                "verbose_name": "status change log",
                "verbose_name_plural": "status change logs",
            },
        ),
        migrations.AlterField(
            model_name="feedback",
            name="created_on",
            field=models.DateTimeField(
                auto_now_add=True,
                help_text="Date of feedback creation",
                verbose_name="created",
            ),
        ),
        migrations.AlterField(
            model_name="feedback",
            name="personal_data",
            field=models.OneToOneField(
                default=None,
                help_text="Author's personal data",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="feedback",
                to="feedback.personaldata",
                verbose_name="personal data",
            ),
        ),
        migrations.AlterField(
            model_name="feedback",
            name="status",
            field=models.CharField(
                choices=[
                    ("received", "received"),
                    ("in processing", "in processing"),
                    ("response given", "response given"),
                ],
                default="received",
                help_text="Processing status",
                max_length=20,
                verbose_name="processing status",
            ),
        ),
        migrations.AlterField(
            model_name="feedback",
            name="text",
            field=models.TextField(
                help_text="Feedback content", max_length=10240, verbose_name="text"
            ),
        ),
        migrations.AlterField(
            model_name="personaldata",
            name="email",
            field=models.EmailField(
                help_text="Feedback author's email",
                max_length=200,
                verbose_name="email",
            ),
        ),
        migrations.AlterField(
            model_name="personaldata",
            name="name",
            field=models.TextField(
                blank=True,
                help_text="Feedback author",
                max_length=100,
                null=True,
                verbose_name="name",
            ),
        ),
        migrations.AlterField(
            model_name="personaldata",
            name="user",
            field=models.ForeignKey(
                blank=True,
                help_text="User who submitted the feedback",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
        migrations.AlterField(
            model_name="statuslog",
            name="feedback",
            field=models.ForeignKey(
                help_text="Feedback for which the status was changed",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="status_logs",
                to="feedback.feedback",
                verbose_name="feedback",
            ),
        ),
        migrations.AlterField(
            model_name="statuslog",
            name="from_status",
            field=models.CharField(
                db_column="from",
                help_text="From which status",
                max_length=20,
                verbose_name="from status",
            ),
        ),
        migrations.AlterField(
            model_name="statuslog",
            name="timestamp",
            field=models.DateTimeField(
                auto_now_add=True,
                help_text="Time of status change",
                verbose_name="time",
            ),
        ),
        migrations.AlterField(
            model_name="statuslog",
            name="to",
            field=models.CharField(
                db_column="to",
                help_text="To which status",
                max_length=20,
                verbose_name="to status",
            ),
        ),
        migrations.AlterField(
            model_name="statuslog",
            name="user",
            field=models.ForeignKey(
                db_column="User_key",
                help_text="User who changed the status",
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="status_logs",
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
    ]
