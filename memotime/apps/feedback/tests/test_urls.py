import http

import django.test
import django.urls
import parametrize

__all__ = ()


class StaticURLTests(django.test.TestCase):
    def setUp(self):
        self.client = django.test.Client()

    def assert_response_status(self, response, expected_status, url):
        self.assertEqual(
            response.status_code,
            expected_status,
            f"Expected status {expected_status} for '{url}' but got:"
            f" {response.status_code}",
        )

    @parametrize.parametrize(
        "url,expected_status",
        [
            (django.urls.reverse("feedback:feedback"), http.HTTPStatus.OK),
        ],
    )
    def test_feedback_url(self, url, expected_status):
        response = self.client.get(url, follow=True)
        self.assert_response_status(response, expected_status, url)
