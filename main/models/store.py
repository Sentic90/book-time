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
    billing_address2 = models.CharField(max_length=60, blank=True)
    billing_zip_code = models.CharField(max_length=12)
    billing_city = models.CharField(max_length=60)
    billing_country = models.CharField(max_length=3)
    shipping_name = models.CharField(max_length=60)
    shipping_address1 = models.CharField(max_length=60)
    shipping_address2 = models.CharField(max_length=60, blank=True)
    shipping_zip_code = models.CharField(max_length=12)
    shipping_city = models.CharField(max_length=60)
    shipping_country = models.CharField(max_length=3)
    date_updated = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)


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
