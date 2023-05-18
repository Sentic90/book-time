import factory
from factory import fuzzy
from . import models


class UserFactory(factory.django.DjangoModelFactory):
    email = 'user@site.com'

    class Meta:
        model = models.User
        django_get_or_create = ['email']


class ProductFactory(factory.django.DjangoModelFactory):
    price = fuzzy.FuzzyDecimal(low=1.0, high=1000.0, precision=2)

    class Meta:
        model = models.Product


class AddressFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Address
