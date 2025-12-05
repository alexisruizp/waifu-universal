from django.test import TestCase
from django.urls import reverse
from gallery.views import parse_waifu_info
import os
from django.conf import settings

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

    def test_parse_waifu_info(self):
        # Test parsing function
        info = parse_waifu_info()
        self.assertIsInstance(info, dict)

    def test_set_featured(self):
        response = self.client.get(reverse('set_featured', args=['Test Waifu']))
        self.assertEqual(response.status_code, 302)  # Redirect
        # Check if file was written
        featured_file = os.path.join(settings.BASE_DIR, 'featured_waifu.txt')
        if os.path.exists(featured_file):
            with open(featured_file, 'r') as f:
                content = f.read().strip()
                self.assertEqual(content, 'Test Waifu')
