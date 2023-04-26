from django.test import TestCase
from unittest.mock import patch
from django.contrib import auth
from decimal import Decimal
from django.urls import reverse
from main.forms import ContactForm, UserCreationForm
from main.models import Product, User, Address, Basket, BasketLine


class TestPage(TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

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

    def test_user_signup_page_loads_correctly(self):
        response = self.client.get(reverse("signup"))  # request Instance
        self.assertEqual(response.status_code, 200)  # Response code == 200
        self.assertTemplateUsed(response, "signup.html")  # if signup.html used
        # check if it's contain BookTime
        self.assertContains(response, "BookTime")
        # check if it's Instance of Form
        self.assertIsInstance(
            response.context["form"], UserCreationForm
        )

    def test_user_signup_page_submission_works(self):
        post_data = {  # request.POST
            "email": "user@domain.com",
            "password1": "abcabcabc",
            "password2": "abcabcabc",
        }

        with patch.object(UserCreationForm, "send_mail") as mock_send:
            response = self.client.post(
                reverse('signup'), post_data)  # Act like HTTP-CLIENT

            # Successfull registration & redirect user with Code 302
            self.assertEqual(response.status_code, 302)
            self.assertTrue(
                User.objects
                .filter(email="user@domain.com")
                .exists()
            )

            self.assertTrue(auth.get_user(self.client).is_authenticated)

            mock_send.assert_called_once()

    def test_address_list_page_reutrn_only_owned(self):
        user1 = User.objects.create_user(
            'user1', "pssw1234"
        )

        user2 = User.objects.create_user(
            'user2', 'pssw12345'
        )

        Address.objects.create(
            user=user1,
            name="Ali Muhammed",
            address1='Flat 1',
            city="KHA",
            country="SD"
        )
        Address.objects.create(
            user=user2,
            name="Ali Muhammed2",
            address1='Flat 2',
            city="KHA",
            country="SD"
        )

        # login user2
        self.client.force_login(user1)
        response = self.client.get(reverse("address_list"))

        self.assertEqual(response.status_code, 200)

        address_list = Address.objects.filter(user=user1)
        self.assertEqual(list(response.context["object_list"]),
                         list(address_list),)

    def test_address_create_stores_user(self):
        user1 = User.objects.create_user("user1", "pw432joij")
        post_data = {
            "name": "Ali Muhammed",
            "address1": "1 KHT st 15",
            "address2": "",
            "zip_code": "1111",
            "city": "Omdurman",
            "country": "SD",
        }
        self.client.force_login(user1)
        self.client.post(reverse("address_create"), post_data)
        self.assertTrue(Address.objects.filter(user=user1).exists())

    def test_add_to_basket_loggedin_works(self):  # TODO not work
        user1 = User.objects.create_user(
            email="user1@domain.com",
            password="passwd123"
        )
        cb = Product.objects.create(
            name="The cathedral and the bazaar",
            slug="cathedral-bazaar",
            price=Decimal("10.00"),
        )

        ws = Product.objects.create(
            name="Microsoft Windows guide",
            slug="microsoft-windows-guide",
            price=Decimal("12.00"),
        )

        self.client.force_login(user1)
        response = self.client.get(
            reverse('add_to_basket'), {"product_id": cb.id})
        response = self.client.get(
            reverse('add_to_basket'), {'product_id': ws.id})
        self.assertTrue(
            Basket.objects.filter(user=user1).exists()
        )
        self.assertEqual(BasketLine.objects
                         .filter(basket__user=user1)
                         .count(), 1)

        self.client.get(
            reverse("add_to_basket"), {"product_id": ws.id}
        )
        self.assertEqual(
            BasketLine.objects.filter(basket__user=user1).count(), 2
        )

    def test_add_to_basket_login_merge_works(self):  # TODO not work
        user1 = User.objects.create_user(
            "user1@domain.com", "pw432joij"
        )
        cb = Product.objects.create(
            name="The cathedral and the bazaar",
            slug="cathedral-bazaar",
            price=Decimal("10.00"),
        )
        w = Product.objects.create(
            name="Microsoft Windows guide",
            slug="microsoft-windows-guide",
            price=Decimal("12.00"),
        )
        basket = Basket.objects.create(user=user1)
        BasketLine.objects.create(basket=basket, product=cb, quantity=2)
        response = self.client.get(
            reverse("add_to_basket"), {"product_id": w.id})
        response = self.client.post(
            reverse("login"), {"email": "user1@a.com", "password": "pw432joij"},)
        self.assertTrue(auth.get_user(self.client).is_authenticated)
        self.assertTrue(Basket.objects.filter(user=user1).exists())
        basket = Basket.objects.get(user=user1)
        self.assertEquals(basket.count(), 3)
