import asyncio
from celery import shared_task
import django.utils.timezone
import datetime
import pytz
import django.core.mail
import django.conf
import django.contrib.auth
import apps.schedule.models as schedule_models
import bot

User = django.contrib.auth.get_user_model()


def send_mail(event, recipient):
    subject = f"Event Reminder: {event.heading}"
    message = (
        f"Scheduled for {event.time_start} on {event.get_day_number_display()}.\n"
        f"Description: {event.description}"
    )
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #FF9500;">Event Reminder: {event.heading}</h2>
            <p>{message}</p>
            <hr style="border: 1px solid #2E3A59;">
            <p style="font-size: 12px; color: #777;">
                This is an automated message. Please do not reply directly to this email.
            </p>
        </body>
    </html>
    """
    email = django.core.mail.EmailMessage(
        subject=subject,
        body=html_message,
        from_email=django.conf.settings.EMAIL_HOST_USER,
        to=[recipient],
    )
    email.content_subtype = "html"
    email.send(fail_silently=True)


def send_telegram(event, chat_id):
    message = (
        f"Reminder: {event.heading}\n"
        f"Scheduled for {event.time_start} on {event.get_day_number_display()}.\n"
        f"Description: {event.description}"
    )
    asyncio.run(bot.send_telegram_message(chat_id, message))


@shared_task
def send_event_reminder(event_id):
    try:
        event = schedule_models.Event.objects.get(id=event_id)
        user = event.user
        now = django.utils.timezone.now()
        user_timezone = (
            pytz.timezone(user.timezone) if hasattr(user, "timezone") else pytz.UTC
        )
        now_in_user_timezone = now.astimezone(user_timezone)
        current_weekday = now_in_user_timezone.isoweekday()
        event_day = event.day_number
        if current_weekday != event_day:
            return (
                f"Reminder not sent for event {event.id} - wrong day (expected"
                f" {event_day}, got {current_weekday})."
            )

        current_time = now_in_user_timezone.time()
        event_time = event.time_start
        event_datetime = django.utils.timezone.make_aware(
            datetime.datetime.combine(now_in_user_timezone.date(), event_time),
            user_timezone,
        )
        time_difference = (now - event_datetime).total_seconds()
        if not (-60 <= time_difference <= 60):
            return (
                f"Reminder not sent for event {event.id} - time mismatch (expected"
                f" {event_time}, got {current_time})."
            )

        email_sent = telegram_sent = False

        if user.is_telegram_subscribed and user.telegram_id:
            send_telegram(event, user.telegram_id)
            telegram_sent = True

        if user.is_email_subscribed:
            send_mail(event, user.email)
            email_sent = True

        if not (email_sent or telegram_sent):
            return (
                f"Reminder not sent for event {event.id} - user {user.id} not"
                " subscribed to any notifications."
            )

        if not event.disposable:
            next_event_datetime = event_datetime + datetime.timedelta(days=7)
            next_event_datetime_utc = next_event_datetime.astimezone(pytz.UTC)
            send_event_reminder.apply_async(
                args=[event.id],
                eta=next_event_datetime_utc,
            )
            return (
                f"Reminder sent for event {event.id} (email: {email_sent}, telegram:"
                f" {telegram_sent}), next reminder scheduled for {next_event_datetime}."
            )

        event.delete()
        return f"Reminder sent for event {event.id} and deleted (disposable)."

    except schedule_models.Event.DoesNotExist:
        return f"Event {event_id} not found."
    except Exception as e:
        return f"Error sending reminder for event {event_id}: {str(e)}"


__all__ = ()
