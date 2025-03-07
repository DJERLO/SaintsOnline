import datetime
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from requests import session
import stripe
from taggit.models import Tag, TaggedItem
from core.models import Product, Coupon, Category, Vendor, CartOrder, CartOrderProducts, ProductImages, ProductReview, Address
from userauths.models import ContactUs, Profile
from core.forms import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib import admin
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.auth.decorators import login_required

import calendar
from django.utils.timezone import localtime
from django.db.models import Count, Avg
from django.db.models.functions import ExtractMonth
from django.core import serializers
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def index(request):
    #products = Product.objects.all().order_by('-id')
    products = Product.objects.filter(product_status="publish", featured=True)

    context = {
        "products": products
    }

    return render(request, 'core/index.html', context)

def product_list_view(request):
    products = Product.objects.filter(product_status="publish")

    context = {
        "products": products
        
    }

    return render(request, 'core/product-list.html', context)

def category_list_view(request):
    categories = Category.objects.all()

    context = {
        "categories":categories
    }
    return render(request, 'core/category-list.html', context)

def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status="publish", category=category)

    context = {
        "category": category,
        "products": products,
    }
    return render(request, 'core/category-product-list.html', context)

def vendor_list_view(request):
    vendors = Vendor.objects.all()
   
    context = {
        "vendors": vendors,
    }

    return render(request, 'core/vendor-list.html', context)

def vendor_detail_view(request, vid):

    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(product_status="publish", vendor=vendor)
    
    context = {
        "vendor": vendor,
        "products": products,
    }

    return render(request, 'core/vendor-detail.html', context)

def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)
    # Get related products based on tags (excluding the current product)
    related_by_tags = Product.objects.filter(tags__in=product.tags.all()).exclude(pid=pid)
    # products = get_object_or_404(Product, pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)
    
    # Combine category-related and tag-related products (remove duplicates)
    related_products = (products | related_by_tags).distinct()
    

    # Getting all reviews
    reviews = ProductReview.objects.filter(product=product)

    # Getting average reviews
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    # Product Review Form
    review_form = ProductReviewForm()

    make_review = True 

    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()

        if user_review_count > 0:
            make_review = False
    


    p_image = product.p_images.all()

    context = {
        "p": product,
        "make_review": make_review,
        "review_form": review_form,
        "p_image": p_image,
        "average_rating": average_rating,
        "reviews": reviews,
        "products":  products,
        "products": related_products,  
        "tags": product.tags.all(), 
    }
    return render(request, 'core/product-detail.html', context)

def tag_list(request, tag_slug=None):
    products = Product.objects.filter(product_status="publish").order_by("-id")

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])
    
    context = {
        "products": products,
        "tag": tag,
    }
    return render(request, 'core/tag.html', context)

def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user
    
    review = ProductReview.objects.create(
        
        user = user,
        product = product,
        review = request.POST['review'],
        rating = request.POST['rating'],
    )

    context = {
        'user': user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
        {
        'bool': True,
        'context': context,
        'average_reviews': average_reviews,
        }
    )

def search_view(request):
    query_title = request.GET.get("q", "")  # Search by title
    query_category = request.GET.get("c", "")  # Search by category ID or name
    query_tag = request.GET.get("tag", "")  # Search by tag name or ID
    
    products = Product.objects.all()  # Start with all products

    if query_title:
            products = products.filter(title__icontains=query_title)

    if query_category:
        products = products.filter(category__name__icontains=query_category)

    if query_tag:
        products = products.filter(tags__name__icontains=query_tag)
        
    context = {
        "query_title": query_title,
        "query_category": query_category,
        "query_tag": query_tag,
        "products": products,
    }
    return render(request, "core/search.html", context)


def filter_products(request):
    categories = request.GET.getlist("category[]")
    vendors = request.GET.getlist("vendor[]")

    # Get min_price and max_price safely, with default values if not present
    min_price = request.GET.get('min_price', 0)  # Default to 0 if not provided
    max_price = request.GET.get('max_price', float('inf'))  # Default to infinity if not provided


    products = Product.objects.filter(product_status="publish").order_by("-id")


    products = products.filter(price__gte=min_price, price__lte=max_price)

    if categories:
        products = products.filter(category__id__in=categories)


    if vendors:
        products = products.filter(vendor__id__in=vendors)

    products = products.distinct()

    data = render_to_string("core/async/product-list.html", {"products": products})
    return JsonResponse({"data": data})

def add_to_cart(request):
    cart_product = {}

    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'image': request.GET['image'],
        'pid': request.GET['pid'],
    }
    
    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:

            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data
    else:
        request.session['cart_data_obj'] = cart_product
    return JsonResponse({"data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj'])})

def cart_view(request):
    cart_total_amount = 0

    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/cart.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("core:index")

def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data
    
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})

def update_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = product_qty
            request.session['cart_data_obj'] = cart_data
    
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})

@login_required
def save_checkout_info(request):
    cart_total_amount = 0
    total_amount = 0
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        country = request.POST.get("country")

        print(full_name)
        print(email)
        print(mobile)
        print(address)
        print(city)
        print(state)
        print(country)

        request.session['full_name'] = full_name
        request.session['email'] = email
        request.session['mobile'] = mobile
        request.session['address'] = address
        request.session['city'] = city
        request.session['state'] = state
        request.session['country'] = country


        if 'cart_data_obj' in request.session:

            # Getting total amount for Paypal Amount
            for p_id, item in request.session['cart_data_obj'].items():
                total_amount += int(item['qty']) * float(item['price'])


            full_name = request.session['full_name']
            email = request.session['email']
            phone = request.session['mobile']
            address = request.session['address']
            city = request.session['city']
            state = request.session['state']
            country = request.session['country']

            # Create ORder Object
            order = CartOrder.objects.create(
                user=request.user,
                price=total_amount,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                state=state,
                country=country,
            )

            del request.session['full_name']
            del request.session['email']
            del request.session['mobile']
            del request.session['address']
            del request.session['city']
            del request.session['state']
            del request.session['country']

            # Getting total amount for The Cart
            for p_id, item in request.session['cart_data_obj'].items():
                cart_total_amount += int(item['qty']) * float(item['price'])

                cart_order_products = CartOrderProducts.objects.create(
                    order=order,
                    order_no="#" + str(order.oid), 
                    item=item['title'],
                    image=item['image'],
                    qty=item['qty'],
                    price=item['price'],
                    total=float(item['qty']) * float(item['price'])
                )



        return redirect("core:checkout", order.oid)
    return redirect("core:checkout", order.oid)


@csrf_exempt
def create_checkout_session(request, oid):
    order = CartOrder.objects.get(oid=oid)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        customer_email = order.email,
        payment_method_types=['card'],
        line_items = [
            {
                'price_data': {
                    'currency': 'PHP',
                    'product_data': {
                        'name': order.full_name
                    },
                    'unit_amount': int(order.price * 100)
                },
                'quantity': 1
            }
        ],
        mode = 'payment',
        success_url = request.build_absolute_uri(reverse("core:payment-completed", args=[order.oid])) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url = request.build_absolute_uri(reverse("core:payment-completed", args=[order.oid]))
    )

    order.paid_status = False
    order.stripe_payment_intent = checkout_session['id']
    order.save()

    print("checkkout session", checkout_session)
    return JsonResponse({"sessionId": checkout_session.id})

@login_required
def checkout(request, oid):
    order = CartOrder.objects.get(oid=oid)
    order_items = CartOrderProducts.objects.filter(order=order)
    
    # Use secret API key to create a Checkout Session
    username = os.getenv("PAYMONGO_SECRET_KEY")
    password = ""
    credentials = f"{username}:{password}"
    authorization = base64.b64encode(credentials.encode()).decode()

    if request.method == "POST":
        code = request.POST.get("code")
        print("code ========", code)
        coupon = Coupon.objects.filter(code=code, active=True).first()
        if coupon:
            if coupon in order.coupons.all():
                messages.warning(request, "Coupon already activated")
                return redirect("core:checkout", order.oid)
            else:
                discount = order.price * coupon.discount / 100 

                order.coupons.add(coupon)
                order.price -= discount
                order.saved += discount
                order.save()

                messages.success(request, "Coupon Activated")
                return redirect("core:checkout", order.oid)
        else:
            messages.error(request, "Coupon Does Not Exists")

        

    context = {
        "oid": oid,
        "order": order,
        "order_items": order_items,
        "stripe_publishable_key": settings.STRIPE_PUBLIC_KEY,
        "authorization": authorization
    }
    return render(request, "core/checkout.html", context)

@login_required 
def payment_completed_view(request, oid=None):
    cart_total_amount = 0
    cart_data = request.session.get('cart_data_obj', {})
    
    # Calculate the cart total amount
    for p_id, item in cart_data.items():
        qty = int(item.get('qty', 0))
        price = float(item.get('price', 0.0))
        cart_total_amount += qty * price

    # If an order ID (oid) is provided, handle it as a paid order
    order = None
    if oid:
        try:
            order = CartOrder.objects.get(oid=oid)
            order.paid_status = True
            order.save()
        except CartOrder.DoesNotExist:
            # Handle the case where the order is not found
            context = {"message": "Order not found Please repeat the process."}
            return render(request, 'core/payment-failed.html', context)

    if 'cart_data_obj' in request.session:
        request.session['cart_data_obj'] = {}  # Clears all items but keeps the key
        request.session.modified = True  # Ensure session updates
    # Prepare the context for the template
    context = {
        "order": order,
        "stripe_publishable_key": settings.STRIPE_PUBLIC_KEY if oid else None,
        "cart_data": cart_data,
        "totalcartitems": len(cart_data),
        "cart_total_amount": cart_total_amount,
    }
    
    return render(request, 'core/payment-completed.html', context)


@login_required
def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')

from django.db.models import Count, F, Func
from datetime import datetime

@login_required
def customer_dashboard(request):
    orders_list = CartOrder.objects.filter(user=request.user).order_by("-id")
    address = Address.objects.filter(user=request.user)

    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    # Initialize month and order count tracking
    month_counts = {}

    # Loop through orders and aggregate counts by month
    for order in orders_list:
        # Get the month number (1 to 12)
        month_number = int(order.order_date.strftime('%m'))
        # Map month number to month name
        month_name = months[month_number - 1]

        # Update count in dictionary
        if month_name in month_counts:
            month_counts[month_name] += 1
        else:
            month_counts[month_name] = 1

    # Separate keys and values for context
    month = list(month_counts.keys())
    total_orders = list(month_counts.values())

    if request.method == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")

        new_address = Address.objects.create(
            user=request.user,
            address=address,
            mobile=mobile,
        )
        messages.success(request, "Address Added Successfully.")
        return redirect("core:dashboard")
    else:
        print("Error")

    # Fetch the user profile, and handle the case where it doesn't exist
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        user_profile = None  # Handle this case as needed

    # Print to debug if needed
    print("User profile is:", user_profile)

    context = {
        "user_profile": user_profile,
        "orders_list": orders_list,
        "address": address,
        "month_counts": month_counts,
        "month": month,
        "total_orders": total_orders,
    }

    return render(request, 'core/dashboard.html', context)


def order_detail(request, id):
    order = CartOrder.objects.get(user=request.user, id=id)
    order_items = CartOrderProducts.objects.filter(order=order)

    
    context = {
        "order_items": order_items,
        
    }
    return render(request, 'core/order-detail.html', context)


def make_address_default(request):
    id = request.GET['id']
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean": True})

# Other Pages 
def contact(request):
    return render(request, "core/contact.html")


def ajax_contact_form(request):
    full_name = request.GET['full_name']
    email = request.GET['email']
    year = request.GET['year']
    phone = request.GET['phone']
    subject = request.GET['subject']
    message = request.GET['message']

    contact = ContactUs.objects.create(
        full_name=full_name,
        email=email,
        year=year,
        phone=phone,
        subject=subject,
        message=message,
    )

    data = {
        "bool": True,
        "message": "Message Sent Successfully"
    }

    return JsonResponse({"data":data})

# Purchase Guide for Customer
def purchase_guide(request):
    return render(request, "core/purchase_guide.html")

# Privacy Policy Guide for Customer
def privacy_policy(request):
    return render(request, "core/privacy_policy.html")

# Terms and Conditions Guide for Customer
def terms_of_service(request):
    return render(request, "core/terms_of_service.html")
