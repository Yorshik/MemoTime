import django.test
import django.urls

import apps.feedback.models as feedback_models

__all__ = ()


class FeedbackModelTests(django.test.TestCase):
    def setUp(self):
        self.feedback_data = {
            "author_name": "Тест",
            "author_mail": "test@example.com",
            "feedback_text": "test_message",
        }

    def tearDown(self):
        feedback_models.Feedback.objects.all().delete()
        feedback_models.PersonalData.objects.all().delete()
        super().tearDown()

    def test_feedback_creation(self):
        personal_data = feedback_models.PersonalData.objects.create(
            name=self.feedback_data["author_name"],
            mail=self.feedback_data["author_mail"],
        )
        feedback = feedback_models.Feedback.objects.create(
            personal_data=personal_data,
            text=self.feedback_data["feedback_text"],
        )
        self.assertEqual(
            feedback.personal_data.name,
            self.feedback_data["author_name"],
        )
        self.assertEqual(
            feedback.personal_data.mail,
            self.feedback_data["author_mail"],
        )
        self.assertEqual(feedback.text, self.feedback_data["feedback_text"])
