import django.test
import django.urls


class TestHomepage(django.test.TestCase):
    def test_homepage_end_point(self):
        response = django.test.Client().get(django.urls.reverse("homepage:homepage"))
        self.assertEqual(response.status_code, 200)


__all__ = ()
