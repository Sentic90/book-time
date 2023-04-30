import logging
from django.db import models
from django.core import exceptions
from django.core.validators import MinValueValidator
from . import User


logger = logging.getLogger(__name__)


class ActiveManager(models.Manager):
    def active(self):

        return super().filter(active=True)


class ProductTagManager(models.Manager):

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Product(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    slug = models.SlugField(max_length=48)
    active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=True)

    tags = models.ManyToManyField('ProductTag')
    objects = ActiveManager()

    def __str__(self) -> str:
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='product-images')
    thumbnail = models.ImageField(
        upload_to='product-thumnails', null=True
    )


class ProductTag(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=48)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    objects = ProductTagManager()

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)


class Basket(models.Model):
    OPEN = 10
    SUBMITTED = 20
    STATUSES = [
        (OPEN, "Open"),
        (SUBMITTED, "Submitted")
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    status = models.IntegerField(choices=STATUSES, default=OPEN)

    def __str__(self):
        return str(self.pk)

    def is_empty(self):
        return self.basketline_set.all().count() == 0

    def count(self):
        return sum([i.quantity for i in self.basketline_set.all()])

    def create_order(self, billing_address, shipping_address):
        if not self.user:
            raise exceptions.BasketExceptions(
                "Cannot create order without user."
            )
        logger.info(
            logger.info(
                "Creating order for basket_id=%d"
                ", shipping_address_id=%d, billing_address_id=%d",
                self.id,
                shipping_address.id,
                billing_address.id,
            )
        )

        order_data = {
            "user": self.user,
            "billing_name": billing_address.name,
            "billing_address1": billing_address.address1,
            "billing_address2": billing_address.address2,
            "billing_zip_code": billing_address.zip_code,
            "billing_city": billing_address.city,
            "billing_country": billing_address.country,
            "shipping_name": shipping_address.name,
            "shipping_address1": shipping_address.address1,
            "shipping_address2": shipping_address.address2,
            "shipping_zip_code": shipping_address.zip_code,
            "shipping_city": shipping_address.city,
            "shipping_country": shipping_address.country
        }

        order = Order.objects.create(**order_data)
        counter = 0
        for line in self.basketline_set.all():
            for item in range(line.quantity):
                order_item_data = {
                    "order": order,
                    "product": line.product,
                }
                order_item = OrderItem.objects.create(
                    **order_item_data
                )
                counter += 1
        logger.info(
            "Created order with id=%d and lines_count=%d", order.id, counter
        )

        self.status = Basket.SUBMITTED
        self.save()
        return order


class BasketLine(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )

    def __str__(self) -> str:
        return str(self.pk)


class Order(models.Model):
    NEW = 10
    PAID = 20
    DONE = 30
    STATUSES = ((NEW, "New"), (PAID, "Paid"), (DONE, "Done"))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUSES, default=NEW)
    billing_name = models.CharField(max_length=60)
    billing_address1 = models.CharField(max_length=60)
    billing_address2 = models.CharField(max_length=60, blank=True, null=True)
    billing_zip_code = models.CharField(max_length=12)
    billing_city = models.CharField(max_length=60)
    billing_country = models.CharField(max_length=3)
    shipping_name = models.CharField(max_length=60)
    shipping_address1 = models.CharField(max_length=60)
    shipping_address2 = models.CharField(max_length=60, blank=True, null=True)
    shipping_zip_code = models.CharField(max_length=12)
    shipping_city = models.CharField(max_length=60)
    shipping_country = models.CharField(max_length=3)
    date_updated = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.items)


class OrderItem(models.Model):
    NEW = 10
    PROCESSING = 20
    SENT = 30
    CANCELLED = 40
    STATUSES = [
        (NEW, "New"),
        (PROCESSING, "Processing"),
        (SENT, "Sent"),
        (CANCELLED, "Cancelled"),
    ]
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    status = models.IntegerField(choices=STATUSES, default=NEW)

    def __str__(self) -> str:
        return self.product.name
