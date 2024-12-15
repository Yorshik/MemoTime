import django.test
import django.urls

import apps.feedback.forms

__all__ = ()


class FeedbackContextTests(django.test.TestCase):
    def setUp(self):
        self.client = django.test.Client()

    def test_author_form_instance(self):
        response = self.client.get(django.urls.reverse("feedback:feedback"))
        self.assertIsInstance(
            response.context["form"]["author"],
            apps.feedback.forms.AuthorForm,
            "Author form should be an instance of AuthorForm",
        )

    def test_feedback_form_instance(self):
        response = self.client.get(django.urls.reverse("feedback:feedback"))
        self.assertIsInstance(
            response.context["form"]["feedback"],
            apps.feedback.forms.FeedbackForm,
            "Feedback form should be an instance of FeedbackForm",
        )
