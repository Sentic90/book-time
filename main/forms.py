import logging
from django import forms
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField

from . import models, widgets
logger = logging.getLogger(__name__)


BasketLineFormSet = forms.inlineformset_factory(
    models.Basket,
    models.BasketLine,
    fields=("quantity",),
    extra=0,
    widgets={"quantity": widgets.PlusMinusNumberInput()},
)


class AddressSelectionForm(forms.Form):
    billing_address = forms.ModelChoiceField(queryset=None)
    shipping_address = forms.ModelChoiceField(queryset=None)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = models.Address.objects.filter(user=user)
        self.fields['billing_address'].queryset = queryset
        self.fields['shipping_address'].queryset = queryset


class ContactForm(forms.Form):
    name = forms.CharField(label='Your name', max_length=100)
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


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = models.User
        fields = ['email']
        fields_classes = {"email": UsernameField}

    def send_mail(self):
        email = self.cleaned_data["email"]
        message = "Welcome{}".format(email)
        logger.info(
            "Sending signup email for email=%s",
            email,
        )
        send_mail(
            "Welcome to BookTime",
            message,
            "site@booktime.domain",
            [email],
            fail_silently=True
        )


class AuthenticationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(
        strip=False, widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user = authenticate(
                self.request, email=email, password=password
            )

            if self.user is None:
                raise forms.ValidationError(
                    "invalid email or password"
                )
                # TODO get Device info & IP
                # logger.warning(
                #     "Authentication failed user"
                # )
            logger.info(
                "Authentication successful for email=%s", email
            )
            return self.cleaned_data

    def get_user(self):
        return self.user
