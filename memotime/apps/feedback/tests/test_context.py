import django.test
import django.urls

from apps.feedback.forms import AuthorForm, FeedbackForm, FilesForm

__all__ = ()


class FeedbackContextTests(django.test.TestCase):
    def setUp(self):
        self.client = django.test.Client()

    def test_author_form_instance(self):
        response = self.client.get(django.urls.reverse("feedback:feedback"))
        self.assertIsInstance(
            response.context["form"]["author"],
            AuthorForm,
            "Author form should be an instance of AuthorForm",
        )

    def test_feedback_form_instance(self):
        response = self.client.get(django.urls.reverse("feedback:feedback"))
        self.assertIsInstance(
            response.context["form"]["feedback"],
            FeedbackForm,
            "Feedback form should be an instance of FeedbackForm",
        )

    def test_files_form_instance(self):
        response = self.client.get(django.urls.reverse("feedback:feedback"))
        self.assertIsInstance(
            response.context["form"]["files_form"],
            FilesForm,
            "Files form should be an instance of FilesForm",
        )
