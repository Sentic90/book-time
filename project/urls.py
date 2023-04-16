from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings


from main import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about-us/', TemplateView.as_view(template_name='about_us.html'),
         name='about_us'),
    path('contact-us/', views.ContactUsView.as_view(), name='contact_us'),
    path('products/<slug:tag>/', views.ProductListView.as_view(), name='products'),
    path('admin/', admin.site.urls),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
