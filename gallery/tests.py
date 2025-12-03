from django.test import TestCase
from django.urls import reverse

class GalleryTestCase(TestCase):
    def test_gallery_page(self):
        response = self.client.get(reverse('waifus_gallery'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'WAIFUVERSE')

    def test_add_waifu_page(self):
        response = self.client.get(reverse('add_waifu'))
        self.assertEqual(response.status_code, 200)

    def test_info_page(self):
        response = self.client.get('/info/')
        self.assertEqual(response.status_code, 200)
