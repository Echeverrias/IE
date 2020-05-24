from django.test import TestCase

class TestIeDjangoViews(TestCase):

    def test_home_view(self):
        resp = self.client.get('/', follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertRedirects(resp, '/home/', status_code=301, target_status_code=200)
        self.assertTemplateUsed(resp, 'index.html')

    def test_404_view(self):
        resp = self.client.get('/unknown_page')
        self.assertEqual(resp.status_code, 404)
        self.assertTemplateUsed(resp, '404.html')