from decimal import Decimal

from django.test import TestCase

from main import models


class TestModel(TestCase):

    def test_active_manager_work(self):
        models.Product.objects.create(
            name="The cathedral and the bazaar",
            price=Decimal("10.00")
        )
        models.Product.objects.create(
            name="Pride and Prejudice",
            price=Decimal("2.00")
        )
        models.Product.objects.create(
            name="A Tale of Two Cities",
            price=Decimal("2.00"),
            active=False
        )
        self.assertEqual(len(models.Product.objects.active()), 2)

    def test_create_order_works(self):
        prodcut_1 = models.Product.objects.create(
            name="The cathedral and the bazaar",
            price=Decimal("10.00"),
        )
        product_2 = models.Product.objects.create(
            name="Pride and Prejudice", price=Decimal("2.00")
        )
        user1 = models.User.objects.create_user(
            "user1", "pw432joij"
        )
        billing = models.Address.objects.create(
            user=user1,
            name="Ali Muhammed",
            address1="127 Strudel road",
            city="Sudan",
            country="SD",
        )
        shipping = models.Address.objects.create(
            user=user1,
            name="Ali Muhammed",
            address1="123 Deacon road",
            city="Sudan",
            country="SD",
        )

        basket = models.Basket.objects.create(user=user1)
        models.BasketLine.objects.create(basket=basket, product=prodcut_1)
        models.BasketLine.objects.create(basket=basket, product=product_2)
        with self.assertLogs("main.models", level="INFO") as cm:

            order = basket.create_order(billing, shipping)
        self.assertGreaterEqual(len(cm.output), 1)
        order.refresh_from_db()

        self.assertEquals(order.user, user1)
        self.assertEquals(order.billing_address1, "127 Strudel road")
        self.assertEquals(order.shipping_address1, "123 Deacon road")

        self.assertEquals(order.items.all().count(), 2)
        lines = order.items.all()
        self.assertEquals(lines[0].product, prodcut_1)
        self.assertEquals(lines[1].product, product_2)
