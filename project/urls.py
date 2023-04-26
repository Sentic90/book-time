from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.conf.urls.static import static
from django.conf import settings

from main import views
from main import forms
from main.models import Product

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('singup/', views.SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html',
         form_class=forms.AuthenticationForm), name='login'),
    path('about-us/', TemplateView.as_view(template_name='about_us.html'),
         name='about_us'),
    path('contact-us/', views.ContactUsView.as_view(), name='contact_us'),
    path('products/<slug:tag>/', views.ProductListView.as_view(), name='products'),
    path('product/<slug:slug>/', DetailView.as_view(model=Product), name='product'),
    path("address/", views.AddressListView.as_view(), name="address_list",),
    path("address/create/", views.AddressCreateView.as_view(),
         name="address_create",),
    path("address/<int:pk>/", views.AddressUpdateView.as_view(),
         name="address_update",),
    path("address/<int:pk>/delete/",
         views.AddressDeleteView.as_view(), name="address_delete",),
    path("add_to_basket/", views.add_to_basket, name="add_to_basket"),
    path('basket/', views.manage_basket, name="basket"),
    path('admin/', admin.site.urls),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
