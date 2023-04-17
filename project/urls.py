from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.conf.urls.static import static
from django.conf import settings


from main import views
from main.models import Product

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about-us/', TemplateView.as_view(template_name='about_us.html'),
         name='about_us'),
    path('contact-us/', views.ContactUsView.as_view(), name='contact_us'),
    path('products/<slug:tag>/', views.ProductListView.as_view(), name='products'),
    path('product/<slug:slug>/', DetailView.as_view(model=Product), name='product'),
    path('admin/', admin.site.urls),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
