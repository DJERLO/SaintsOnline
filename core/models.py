from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone


STATUS_CHOICES = (
    ("processing", "Processing"),
    ("packaging", "Packing"),
    ("Ready To Pickup", "Ready To Pickup"),
    ("All Ready Pickup", "Has been Pickup"),
)

STATUS = (
    ("draft", "Draft"),
    ("disable", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In review"),
    ("publish", "Publish"),
)

RATING = (
    (1, "★☆☆☆☆"),
    (2, "★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),
)

def user_directory_path(instance,filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Food")
    image = models.ImageField(upload_to="category", default="category.jpg")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def product_count(self):
        return Product.objects.filter(category=self).count()

    def __str__(self):
        return self.title


    class Tags(models.Model):
        pass


class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="ven", alphabet="abcdefgh12345")

    title = models.CharField(max_length=100, default="Shop Name Here")
    image = models.ImageField(upload_to=user_directory_path, default="vendor.jpg")
    cover_image = models.ImageField(upload_to=user_directory_path, default="vendor.jpg")
    description = models.TextField(null=True, blank=True, default="SAINT'S STORE")
    address = models.CharField(max_length=100, default="123 Main Street.")
    contact = models.CharField(max_length=100, default="+123 (456) 789")
    chat_resp_time = models.CharField(max_length=100, default="100")
    shipping_on_time = models.CharField(max_length=100, default="100")
    authentic_rating = models.CharField(max_length=100, default="100")
    days_return = models.CharField(max_length=100, default="100")
    warranty_period = models.CharField(max_length=100, default="100")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Shop Management"

    def vendor_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
    
class ProductTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    
class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefgh12345")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="product")
    title = models.CharField(max_length=100, default="Fresh Pear")
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    description = models.TextField(null=True, blank=True, default="This is the product")
    price = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    old_price = models.DecimalField(max_digits=12, decimal_places=2, default="2.99")
    vat = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    specifications = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=100, default="What is the product type?", null=True, blank=True)
    stock_count = models.CharField(max_length=100, default="Item stock count?", null=True, blank=True)
    life = models.CharField(max_length=100, default="item life spand?", null=True, blank=True)
    mfd = models.DateField(auto_now_add=False, null=True, blank=True)

    tags = models.ManyToManyField(ProductTag, blank=True, related_name="products")

    # tags =  models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True)

    product_status = models.CharField(choices=STATUS, max_length=100, default="In Review")
    

    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=True)
    digital = models.BooleanField(default=False)
        
    sku = ShortUUIDField(unique=True, length=4, max_length=10, prefix="sku", alphabet="abcdefgh")

    date = models.DateField(auto_now_add=True)
    updated = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Product"

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

    def get_precentage(self):
        new_price = (self.price / self.old_price) * 100
        return new_price
    
class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, related_name="p_images", on_delete=models.SET_NULL, null=True)
    date =  models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Images"


######################################### Cart, Order, OrderItems And Address #################################################
######################################### Cart, Order, OrderItems And Address #################################################
######################################### Cart, Order, OrderItems And Address #################################################
######################################### Cart, Order, OrderItems And Address #################################################

class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)

    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)    

    price = models.DecimalField(max_digits=12, decimal_places=2, default="1.99")
    vat = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    coupons = models.ManyToManyField("core.Coupon", blank=True)

    shipping_method = models.CharField(max_length=100, null=True, blank=True)

    tracking_id = models.CharField(max_length=100, null=True, blank=True)
    tracking_website_address = models.CharField(max_length=100, null=True, blank=True)

    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=False, null=True, default=timezone.now)
    product_status = models.CharField(choices=STATUS_CHOICES, max_length=30, default="processing")
    sku = ShortUUIDField(null=True, blank=True, length=5, prefix="SKU", max_length=20, alphabet="abcd1234")
    oid = ShortUUIDField(null=True, blank=True, length=8, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now, null=True, blank=True)

    stripe_payment_intent = models.CharField(max_length=1000, null=True, blank=True)

    

    class Meta:
        verbose_name_plural = "Cart Order"


class CartOrderProducts(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    order_no = models.CharField(max_length=200)
    oid = ShortUUIDField(null=True, blank=True, length=8, max_length=20, alphabet="1234567890")

    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)

    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default="1.99")
    total = models.DecimalField(max_digits=12, decimal_places=2, default="1.99")

    product_status = models.CharField(choices=STATUS_CHOICES, max_length=30, default="processing")

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_img(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.image))


######################################### Product Review, Wishlists, Address #################################################
######################################### Product Review, Wishlists, Address #################################################
######################################### Product Review, Wishlists, Address #################################################
######################################### Product Review, Wishlists, Address #################################################


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="reviews")
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date =  models.DateField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Product Reviews"

    def _str_(self):
        return self.prodduct.title
    
    def get_rating(self):
        return self.rating
    

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    mobile = models.CharField(max_length=300, null=True)
    address = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"

class Coupon(models.Model):
    code = models.CharField(max_length=1000)
    discount = models.IntegerField(default=1)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code}"

