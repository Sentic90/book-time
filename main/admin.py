import logging
from datetime import datetime, timedelta
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from django.db.models.functions import TruncDay
from django.db.models import Avg, Count, Min, Sum
from django.http.request import HttpRequest
from django.template.response import TemplateResponse
from django.urls import path
from django.contrib.auth.admin import (UserAdmin as DjangoUserAdmin)
from django.utils.html import format_html
from .models import (Product, ProductTag, ProductImage, Address,
                     User, Basket, BasketLine, Order, OrderItem)

logger = logging.getLogger(__name__)


class UserAdmin(DjangoUserAdmin):
    # User model has a lot of fields, which is why we are
    # reorganizing them for readability
    # in form change page
    add_form_template = 'signup.html'
    fieldsets = [
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")},),
        ("Persmissions", {"fields": ("is_active", "is_staff",
         "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    ]
    # in form add page
    add_fieldsets = [
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2")
        })
    ]

    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_staff",
    ]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["email"]


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'in_stock', 'price')
    list_filter = ('active', 'in_stock', 'date_updated')
    list_editable = ('in_stock', )
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    # autocomplete_fields = ('tags',)
    '''slug is an important field for our site, it is used in
    all the product URLs. We want to limit the ability to
    change this only to the owners of the company.'''

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return list(self.readonly_fields) + ['slug', 'name']

    # This is required for get_readonly_fields to work
    def get_prepopulated_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}


class DispatchersProductAdmin(ProductAdmin):
    readonly_fields = ("description", "price", "tags", "active")
    prepopulated_fields = {}
    autocomplete_fields = ()


class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('active',)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    # autocomplete_fields = ('products',)

# tag slugs also appear in urls, therefore it is a
 # property only owners can change
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return list(self.readonly_fields) + ["slug", "name"]

    def get_prepopulated_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_tag', 'product_name')
    readonly_fields = ('thumbnail',)
    search_fields = ('product__name',)

    # this function returns HTML for the first column defined
    # in the list_display property above
    def thumbnail_tag(self, obj):
        if obj.thumbnail:
            return format_html(
                f'<img src="{obj.thumbnail.url}"/>'
            )
        return '-'

    thumbnail_tag.short_description = "Thumbnail"

    def product_name(self, obj):
        return obj.product.name


class BasketLineInline(admin.TabularInline):
    model = BasketLine
    raw_id_fields = ("product",)


class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "address1",
        "address2",
        "city",
        "country",
    )
    readonly_fields = ("user",)


class BasketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "count")
    list_editable = ("status",)
    list_filter = ("status",)
    inlines = (BasketLineInline,)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    # raw_id_fields = ("product",)
    autocomplete_fields = ['product']


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")
    list_editable = ("status",)
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (OrderItemInline,)

    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Billing info",
            {
                "fields": (
                    "billing_name",
                    "billing_address1",
                    "billing_address2",
                    "billing_zip_code",
                    "billing_city",
                    "billing_country",
                )
            },
        ),
        (
            "Shipping info",
            {"fields": (
                "shipping_name",
                "shipping_address1",
                "shipping_address2",
                "shipping_zip_code",
                "shipping_city",
                "shipping_country",
            )
            },
        ),
    )


'''
    Employees need a custom version of the order views because
#   they are not allowed to change products already purchased
#   without adding and removing lines
'''


class CentralOfficeOrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product']


class CentralOfficeOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")
    list_editable = ("status",)
    readonly_fields = ("user",)
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (CentralOfficeOrderItemInline,)
    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Billing info",
            {
                "fields": (
                    "billing_name",
                    "billing_address1",
                    "billing_address2",
                    "billing_zip_code",
                    "billing_city",
                    "billing_country",
                )
            },
        ),
        (
            "Shipping info",
            {
                "fields": (
                    "shipping_name",
                    "shipping_address1",
                    "shipping_address2",
                    "shipping_zip_code",
                    "shipping_city",
                    "shipping_country",
                )
            },
        ),
    )


# Dispatchers do not need to see the billing address in the fields
class DispatchersOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "shipping_name",
        "date_added",
        "status",
    )
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (CentralOfficeOrderItemInline,)
    fieldsets = (
        "Shipping info",
        {
            "fields": (
                "shipping_name",
                "shipping_address1",
                "shipping_address2",
                "shipping_zip_code",
                "shipping_city",
                "shipping_country",
            )
        },
    ),
    # Dispatchers are only allowed to see orders that
    # are ready to be shipped

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status=Order.PAID)


# The following will add reporting views to the list of
# available urls and will list them from the index page
class ColoredAdminSite(admin.sites.AdminSite):
    def each_context(self, request):
        context = super().each_context(request)
        context["site_header_color"] = getattr(self, "site_header_color", None)
        context["module_caption_color"] = getattr(
            self, "module_caption_color", None)
        return context


class ReportingColoredAdminSite(ColoredAdminSite):
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("orders_per_day/", self.admin_view(self.orders_per_day),)]
        return my_urls + urls

    def orders_per_day(self, request):
        starting_day = datetime.now() - timedelta(days=180)
        order_data = (
            Order.objects.filter(
                date_added__gt=starting_day)
            .annotate(day=TruncDay("date_added"))
            .values('day')
            .annotate(c=Count('id'))
        )
        lables = [x['day'].strftime("%Y-%m-%d") for x in order_data]
        values = [x["c"] for x in order_data]

        context = dict(
            self.each_context(request),
            title="Orders per day",
            lables=lables,
            values=values
        )
        return TemplateResponse(
            request, "orders_per_day.html", context
        )

    def index(self, request, extra_context=None):
        reporting_pages = [
            {
                "name": "Orders per day",
                "link": "orders_per_day/"
            }
        ]
        if not extra_context:
            extra_context = {}
        extra_context = {"reporting_pages": reporting_pages}

        return super().index(request, extra_context)


#  Finally we define 3 instances of AdminSite, each with their own
# set of required permissions and colors

class OwnersAdminSite(ReportingColoredAdminSite):
    site_header = "BookTime owners administration"
    site_header_color = "black"
    module_caption_color = "grey"

    # return True or Flase either has permission to access
    def has_permission(self, request):
        return (request.user.is_active and request.user.is_superuser)


class CentralOfficeAdminSite(ReportingColoredAdminSite):
    site_header = "BookTime central office administration"
    site_header_color = "purple"
    module_caption_color = "pink"

    def has_permission(self, request):
        return (request.user.is_active and request.user.is_employee)


class DispatchersAdminSite(ColoredAdminSite):
    site_header = "BookTime central dispatch administration"
    site_header_color = "green"
    module_caption_color = "lightgreen"

    def has_permission(self, request):
        return (request.user.is_active and request.user.is_dispatcher)


# Owner Permission
main_admin = OwnersAdminSite()
main_admin.register(User, UserAdmin)
main_admin.register(Group, GroupAdmin)
main_admin.register(Product, ProductAdmin)
main_admin.register(ProductTag, ProductTagAdmin)
main_admin.register(ProductImage, ProductImageAdmin)

main_admin.register(Address, AddressAdmin)
main_admin.register(Basket, BasketAdmin)
main_admin.register(Order, OrderAdmin)

# Central Office Permission
central_office_admin = CentralOfficeAdminSite("central-office-admin")
central_office_admin.register(Product, ProductAdmin)
central_office_admin.register(ProductTag, ProductTagAdmin)
central_office_admin.register(ProductImage, ProductImageAdmin)
central_office_admin.register(Address, AddressAdmin)
central_office_admin.register(Order, CentralOfficeOrderAdmin)

# Dispatcher permission
dispatchers_admin = DispatchersAdminSite("dispatchers-admin")
dispatchers_admin.register(Product, DispatchersProductAdmin)
dispatchers_admin.register(ProductTag, ProductTagAdmin)
dispatchers_admin.register(Order, DispatchersOrderAdmin)
