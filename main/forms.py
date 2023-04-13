from django import forms
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


class ContactForm(forms.Form):
    name = forms.CharField(label='Your name', max_length=100, min_length=15)
    message = forms.CharField(
        max_length=600, widget=forms.Textarea
    )

    def send_mail(self):

        # logging goes here
        logger.info("Sending email to customer service")
        message = f"From: {self.cleaned_data['name']} \n {self.cleaned_data['message']}"
        # sending email
        send_mail(
            "Site Message",
            message,
            "site@booktime.domain",
            ["customerservice@boottime.domain"],
            fail_silently=False
        )
