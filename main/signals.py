from io import BytesIO
import logging
from PIL import Image
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

from .models import ProductImage, Basket

THUMBANIL_SIZE = (200, 150)

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def merge_basket_if_found(sender, user, request, **kwargs):
    anonymous_basket = getattr(request, "basket", None)

    if anonymous_basket:
        try:
            logged_in_basket = Basket.objects.get(
                user=user, status=Basket.OPEN
            )
            for line in anonymous_basket.basketline_set.all():
                line.basket = logged_in_basket
                line.save()
            anonymous_basket.delete()
            request.basket = logged_in_basket

            logger.info(
                "Merged basket to id %d", logged_in_basket.id
            )
        except Basket.DoesNotExist:
            anonymous_basket.user = user
            anonymous_basket.save()
            logger.info(
                "Assigned user to basket id %d",
                anonymous_basket.id
            )


@receiver(pre_save, sender=ProductImage)
def generate_thumbnail(sender, instance, *args, **kwargs):
    """
        function to compress image size into
    300x300 
        Logging -> INFO
    """

    logger.info(
        "Generating thumbnail for product %d", instance.product.id
    )

    image = Image.open(instance.image)
    image = image.convert("RGB")
    image.thumbnail(THUMBANIL_SIZE, Image.ANTIALIAS)

    temp_thumb = BytesIO()
    image.save(temp_thumb, "JPEG")
    temp_thumb.seek(0)

    instance.thumbnail.save(
        instance.image.name,
        ContentFile(temp_thumb.read()),
        save=False,
    )
    temp_thumb.close()
