import django.test
import django.urls

import apps.feedback.models

__all__ = ()


class FeedbackModelTests(django.test.TestCase):
    def setUp(self):
        self.feedback_data = {
            "author_name": "Тест",
            "author_email": "test@example.com",
            "feedback_text": "test_message",
        }

    def tearDown(self):
        apps.feedback.models.Feedback.objects.all().delete()
        apps.feedback.models.PersonalData.objects.all().delete()
        super().tearDown()

    def test_feedback_creation(self):
        personal_data = apps.feedback.models.PersonalData.objects.create(
            name=self.feedback_data["author_name"],
            email=self.feedback_data["author_email"],
        )
        feedback = apps.feedback.models.Feedback.objects.create(
            personal_data=personal_data,
            text=self.feedback_data["feedback_text"],
        )
        self.assertEqual(
            feedback.personal_data.name,
            self.feedback_data["author_name"],
        )
        self.assertEqual(
            feedback.personal_data.email,
            self.feedback_data["author_email"],
        )
        self.assertEqual(feedback.text, self.feedback_data["feedback_text"])
