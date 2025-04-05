from django.contrib import admin
from core.models import Coupon, Product, Category, ProductTag, Vendor, CartOrderProducts, ProductImages, ProductReview, Address, CartOrder
from django.contrib import admin
from taggit.models import Tag, TaggedItem

class ProductImageAdmin(admin.TabularInline):
    model = ProductImages

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]
    list_editable = ['title', 'price', 'featured','stock_count', 'product_status']
    list_display = ['product_image', 'title', 'price', 'category', 'cost', 'stock_count','featured', 'product_status', 'pid']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image']

class VendorAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor_image']

class CartOrderAdmin(admin.ModelAdmin):
    list_editable = ['product_status']
    list_display = ['user', 'price', 'paid_status', 'order_date', 'product_status', 'oid']

class CartOrderProductsAdmin(admin.ModelAdmin):
    list_editable = ['product_status']
    list_display = ['order', 'order_no', 'item', 'oid', 'product_status', 'qty', 'total']

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'review', 'rating']


class AddressAdmin(admin.ModelAdmin):
    model = ProductTag

class ProductTagsAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderProducts, CartOrderProductsAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(ProductTag, ProductTagsAdmin)
admin.site.register(Coupon)
