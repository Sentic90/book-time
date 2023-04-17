from django.test import TestCase
from decimal import Decimal
from django.urls import reverse
from main.forms import ContactForm
from main.models import Product


class TestPage(TestCase):
    def test_home_page_work(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'BookTime')

    def test_about_us_page_work(self):
        response = self.client.get(reverse('about_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about_us.html')
        self.assertContains(response, 'BookTime')

    def test_contact_us_page_work(self):
        response = self.client.get(reverse('contact_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_form.html')
        self.assertContains(response, 'BookTime')
        self.assertIsInstance(
            response.context["form"], ContactForm
        )

    def test_products_page_returns_active(self):
        Product.objects.create(
            name="The cathedral and the bazaar",
            slug="cathedral-bazaar",
            price=Decimal("10.00"),
        )

        Product.objects.create(
            name="A Tale of Two Cities",
            slug="tale-two-cities",
            price=Decimal("2.00"),
            active=False,
        )

        response = self.client.get(
            reverse('products', kwargs={'tag': 'all'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BookTime")

        product_list = Product.objects.active().order_by("name")
        self.assertEqual(
            list(response.context["object_list"]), list(product_list))

    def test_products_page_filters_by_tags_and_active(self):
        cb = Product.objects.create(
            name="The cathedral and the bazaar",
            slug="cathedral-bazaar",
            price=Decimal("10.00"),
        )
        cb.tags.create(name="Open source", slug="opensource")
        Product.objects.create(
            name="Microsoft Windows guide",
            slug="microsoft-windows-guide",
            price=Decimal("12.00"),
        )
        response = self.client.get(
            reverse("products", kwargs={"tag": "opensource"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BookTime")

        product_list = (
            Product.objects.active()
            .filter(tags__slug="opensource")
            .order_by("name")
        )
        self.assertEqual(
            list(response.context["object_list"]),
            list(product_list)
        )
