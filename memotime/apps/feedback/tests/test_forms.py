import pathlib
import shutil
import tempfile

import django.conf
import django.test
import django.urls
import parametrize

import apps.feedback.forms
import apps.feedback.models

__all__ = ()


@django.test.override_settings(
    ALLOW_REVERSE=False,
    MEDIA_ROOT=tempfile.mkdtemp(),
)
class FeedbackFormTests(django.test.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.valid_form_data = {
            "author-name": "Тест",
            "author-email": "test@example.com",
            "feedback-text": "test_message",
        }

    def tearDown(self):
        apps.feedback.models.Feedback.objects.all().delete()
        apps.feedback.models.PersonalData.objects.all().delete()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        cls.clean_up_media_root()
        super().tearDownClass()

    @classmethod
    def clean_up_media_root(cls):
        media_root_path = pathlib.Path(django.conf.settings.MEDIA_ROOT)
        if media_root_path.exists():
            shutil.rmtree(django.conf.settings.MEDIA_ROOT)

    @parametrize.parametrize(
        "test_data",
        [
            ({},),
            ({"author-name": "", "author-email": "", "feedback-text": ""},),
        ],
    )
    def test_empty_form_is_invalid(self, test_data):
        response = django.test.Client().post(
            django.urls.reverse("feedback:feedback"),
            data=test_data,
            follow=True,
        )
        self.assertFalse(
            response.context["form"]["author"].is_valid(),
            "Empty author form should be invalid",
        )
        self.assertFalse(
            response.context["form"]["feedback"].is_valid(),
            "Empty feedback form should be invalid",
        )

    @parametrize.parametrize(
        "test_data",
        [
            ({"author-name": "", "author-email": "", "feedback-text": ""},),
        ],
    )
    def test_empty_form_has_one_error_in_author_form(self, test_data):
        response = django.test.Client().post(
            django.urls.reverse("feedback:feedback"),
            data=test_data,
            follow=True,
        )
        self.assertEqual(
            len(response.context["form"]["author"].errors),
            1,
            "Empty author form should have exactly one error",
        )

    @parametrize.parametrize(
        "test_data",
        [
            ({"author-name": "", "author-email": "", "feedback-text": ""},),
        ],
    )
    def test_empty_form_has_one_error_in_feedback_form(self, test_data):
        response = django.test.Client().post(
            django.urls.reverse("feedback:feedback"),
            data=test_data,
            follow=True,
        )
        self.assertEqual(
            len(response.context["form"]["feedback"].errors),
            2,
            "Empty feedback form should have exactly one error",
        )

    @parametrize.parametrize(
        "test_data",
        [
            (
                {
                    "author-name": "Тест",
                    "author-email": "invalid_email",
                    "feedback-text": "test_message",
                },
            ),
        ],
    )
    def test_author_form_email_field_has_error(self, test_data):
        response = self.client.post(
            django.urls.reverse("feedback:feedback"),
            data=test_data,
            follow=True,
        )
        self.assertTrue(
            response.context["form"]["author"].has_error("email"),
            "Form should contain an error for invalid email format",
        )

    @parametrize.parametrize(
        "test_data",
        [
            (
                {
                    "author-name": "Тест",
                    "author-email": "test@example.com",
                    "feedback-text": "",
                },
            ),
        ],
    )
    def test_feedback_form_text_field_has_error(self, test_data):
        response = self.client.post(
            django.urls.reverse("feedback:feedback"),
            data=test_data,
            follow=True,
        )
        self.assertTrue(
            response.context["form"]["feedback"].has_error("text"),
            "Form should contain an error for empty message text",
        )

    def test_count_feedback_increased(self):
        items_count = apps.feedback.models.Feedback.objects.count()
        django.test.Client().post(
            django.urls.reverse("feedback:feedback"),
            data=self.valid_form_data,
            follow=True,
        )
        self.assertEqual(
            apps.feedback.models.Feedback.objects.count(),
            items_count,
            "Feedback count should increase by 1 after successful submission",
        )

    @parametrize.parametrize(
        "form_name, field_name, expected_label",
        [
            ("author", "name", "Name"),
            ("author", "email", "Email"),
            ("feedback", "text", "Description"),
        ],
    )
    def test_field_label(self, form_name, field_name, expected_label):
        form = apps.feedback.forms.ProfileUpdateMultiForm().forms[form_name]
        field_label = form.fields[field_name].label
        self.assertEqual(
            field_label,
            expected_label,
            f"Field {field_name} in {form_name} should have label '{expected_label}'",
        )

    @parametrize.parametrize(
        "form_name, field_name, expected_help_text",
        [
            ("author", "name", "Feedback author"),
            ("author", "email", "Feedback author's email"),
            ("feedback", "text", "Content of your feedback"),
        ],
    )
    def test_field_help_text(self, form_name, field_name, expected_help_text):
        form = apps.feedback.forms.ProfileUpdateMultiForm().forms[form_name]
        field_help_text = form.fields[field_name].help_text
        self.assertEqual(
            field_help_text,
            expected_help_text,
            f"Field {field_name} in {form_name} should have help text"
            f" '{expected_help_text}'",
        )

    def test_form_field_required(self):
        invalid_data = {
            "author-name": "",
            "author-email": "test@example.com",
            "feedback-text": "",
        }
        response = django.test.Client().post(
            django.urls.reverse("feedback:feedback"),
            data=invalid_data,
            follow=True,
        )
        self.assertTrue(
            response.context["form"]["author"].fields["email"].required,
            "The email field must be mandatory",
        )

    def test_form_field_default_value(self):
        response = django.test.Client().get(
            django.urls.reverse("feedback:feedback"),
        )
        self.assertEqual(
            response.context["form"]["author"].fields["name"].initial,
            None,
            "The initial value of the name field should be None",
        )

    def test_form_field_widget_class(self):
        response = django.test.Client().get(
            django.urls.reverse("feedback:feedback"),
        )
        for form_name in ["author", "feedback"]:
            form = response.context["form"][form_name]
            for field in form.visible_fields():
                self.assertIn(
                    "form-control",
                    field.field.widget.attrs.get("class", ""),
                    f"All form fields in {form_name} must have the CSS class"
                    " 'form-control'",
                )
