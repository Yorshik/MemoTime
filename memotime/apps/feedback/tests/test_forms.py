import pathlib
import shutil
import tempfile

import django.conf
import django.core.files.uploadedfile
import django.test
import django.urls
import parametrize

from apps.feedback.forms import ProfileUpdateMultiForm
from apps.feedback.models import Feedback, PersonalData

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
            "author-mail": "test@example.com",
            "feedback-text": "test_message",
            "files_form-files": [],
        }

    def tearDown(self):
        Feedback.objects.all().delete()
        PersonalData.objects.all().delete()
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
            ({"author-name": "", "author-mail": "", "feedback-text": ""},),
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
        self.assertTrue(
            response.context["form"]["files_form"].is_valid(),
            "Empty files form should be valid",
        )

    @parametrize.parametrize(
        "test_data",
        [
            ({"author-name": "", "author-mail": "", "feedback-text": ""},),
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
            ({"author-name": "", "author-mail": "", "feedback-text": ""},),
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
            1,
            "Empty feedback form should have exactly one error",
        )

    @parametrize.parametrize(
        "test_data",
        [
            (
                {
                    "author-name": "Тест",
                    "author-mail": "invalid_email",
                    "feedback-text": "test_message",
                },
            ),
        ],
    )
    def test_author_form_mail_field_has_error(self, test_data):
        response = self.client.post(
            django.urls.reverse("feedback:feedback"),
            data=test_data,
            follow=True,
        )
        self.assertTrue(
            response.context["form"]["author"].has_error("mail"),
            "Form should contain an error for invalid email format",
        )

    @parametrize.parametrize(
        "test_data",
        [
            (
                {
                    "author-name": "Тест",
                    "author-mail": "test@example.com",
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

    def test_successful_message_in_form(self):
        response = django.test.Client().post(
            django.urls.reverse("feedback:feedback"),
            data=self.valid_form_data,
            follow=True,
        )
        self.assertContains(
            response,
            "Спасибо! Ваш отзыв был успешно отправлен.",
            msg_prefix="Success message should be displayed after form submission",
        )

    def test_count_feedback_increased(self):
        items_count = Feedback.objects.count()
        django.test.Client().post(
            django.urls.reverse("feedback:feedback"),
            data=self.valid_form_data,
            follow=True,
        )
        self.assertEqual(
            Feedback.objects.count(),
            items_count + 1,
            "Feedback count should increase by 1 after successful submission",
        )

    def test_redirect_after_successful_submission(self):
        response = django.test.Client().post(
            django.urls.reverse("feedback:feedback"),
            data=self.valid_form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            django.urls.reverse("feedback:feedback"),
            msg_prefix="Should redirect to feedback page after successful submission",
        )

    def test_feedback_models_added(self):
        django.test.Client().post(
            django.urls.reverse("feedback:feedback"),
            data=self.valid_form_data,
            follow=True,
        )
        self.assertTrue(
            Feedback.objects.filter(
                personal_data__name=self.valid_form_data["author-name"],
                text=self.valid_form_data["feedback-text"],
                personal_data__mail=self.valid_form_data["author-mail"],
            ).exists(),
            "Submitted data should be saved in the database",
        )

    def test_uploaded_files_exist(self):
        test_file = django.core.files.uploadedfile.SimpleUploadedFile(
            name="test_file.txt",
            content=b"This is a test file content.",
            content_type="text/plain",
        )
        test_file2 = django.core.files.uploadedfile.SimpleUploadedFile(
            name="test_file2.txt",
            content=b"This is another test file content.",
            content_type="text/plain",
        )
        test_form_data = self.valid_form_data.copy()
        test_form_data["files_form-files"] = [test_file, test_file2]
        django.test.Client().post(
            django.urls.reverse("feedback:feedback"),
            data=test_form_data,
            follow=True,
        )
        created_feedback = Feedback.objects.latest(
            "created_on",
        )
        for uploaded_file in created_feedback.files.all():
            self.assertTrue(
                uploaded_file.file.storage.exists(uploaded_file.file.name),
                "Uploaded files should exist in storage",
            )

    @parametrize.parametrize(
        "form_name, field_name, expected_label",
        [
            ("author", "name", "Имя"),
            ("author", "mail", "Почта"),
            ("feedback", "text", "Описание"),
            ("files_form", "files", "Прикрепленные файлы"),
        ],
    )
    def test_field_label(self, form_name, field_name, expected_label):
        form = ProfileUpdateMultiForm().forms[form_name]
        field_label = form.fields[field_name].label
        self.assertEqual(
            field_label,
            expected_label,
            f"Field {field_name} in {form_name} should have label '{expected_label}'",
        )

    @parametrize.parametrize(
        "form_name, field_name, expected_help_text",
        [
            ("author", "name", "Автор фидбэка"),
            ("author", "mail", "Почта автора фидбэка"),
            ("feedback", "text", "Содержание обращения"),
            ("files_form", "files", ""),
        ],
    )
    def test_field_help_text(self, form_name, field_name, expected_help_text):
        form = ProfileUpdateMultiForm().forms[form_name]
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
            "author-mail": "test@example.com",
            "feedback-text": "",
        }
        response = django.test.Client().post(
            django.urls.reverse("feedback:feedback"),
            data=invalid_data,
            follow=True,
        )
        self.assertTrue(
            response.context["form"]["author"].fields["mail"].required,
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
