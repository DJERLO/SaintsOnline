from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from core.models import CartOrder, CartOrderProducts, Product, Category, ProductReview, ProductTag
from userauths.models import Profile, User
from useradmin.forms import AddProductForm
from useradmin.decorators import admin_required
from django.db.models import F, ExpressionWrapper, DecimalField
from django.contrib.auth.decorators import user_passes_test
import datetime as dt
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import Substr

def is_admin(user):
    return user.groups.filter(name='Staff').exists()
def is_customer(user):
    return user.groups.filter(name='Customer').exists()

@user_passes_test(is_admin)
def dashboard(request):
    user = User.objects.get(id=request.user.id)
    revenue = 0  # Placeholder for total revenue. Replace with actual query when ready.
    
    revenue = CartOrder.objects.filter(paid_status=True).aggregate(price=Sum("price"))
    this_month = dt.datetime.now().month
    monthly_revenue = CartOrder.objects.filter(paid_status=True, order_date__month=this_month).aggregate(price=Sum("price"))
    
    total_orders_count = CartOrder.objects.all()
    all_products = Product.objects.all()
    all_categories = Category.objects.all()
    new_customers = User.objects.all().order_by("-id")[:6]
    latest_orders = CartOrder.objects.all()

    context = {
        "user": user,
        "monthly_revenue": monthly_revenue,
        "revenue": revenue,
        "all_products": all_products,
        "all_categories": all_categories,
        "new_customers": new_customers,
        "latest_orders": latest_orders,
        "total_orders_count": total_orders_count,
    }
    return render(request, "useradmin/dashboard.html", context)

@user_passes_test(is_admin)
def reports(request, recurrent="Yearly"):
    user = request.user
    now = timezone.localtime()
    today = now.date()
    this_week_start = today - dt.timedelta(days=today.weekday())  # Monday
    this_month = now.month
    this_year = now.year

    order = CartOrder.objects.filter(paid_status=True).order_by("-id")

    # Total revenue (all time)
    total_revenue = CartOrder.objects.filter(paid_status=True).aggregate(price=Sum("price"))["price"] or 0

    # Daily revenue
    daily_revenue = CartOrder.objects.filter(paid_status=True, order_date=today).aggregate(price=Sum("price"))["price"] or 0

    # Daily product sales and revenue
    if recurrent == "Daily":
        # Daily revenue
        revenue = CartOrder.objects.filter(paid_status=True, order_date=today).aggregate(price=Sum("price"))["price"] or 0    

         # 🔥 Daily product sales Qty
        sales = CartOrderProducts.objects.filter(
            order__paid_status=True,
            order__order_date__date=today
        ).annotate(
            order_num=Substr('order__oid', 2),  # Remove the '#' symbol (start from the second character)
            qty_sold=Sum('qty'),
            total_sold=Sum('total'),
            total_costing=Sum('cost'),
            order_date=F('order__order_date')  # Accessing the order_date field from CartOrder model
        ).values(
            'item',
            'order_num',  # This will contain the order number without the '#'
            'order_date',  # This will contain the order date
            'qty_sold',
            'total_sold',
            'total_cost'
        )   
    
    if recurrent == "Weekly":
        # Weekly revenue
        revenue = CartOrder.objects.filter(
            paid_status=True,
            order_date__gte=this_week_start,
            order_date__lte=today
        ).aggregate(price=Sum("price"))["price"] or 0
        
        # 🔥 Weekly product sales Qty
        sales = CartOrderProducts.objects.filter(
            order__paid_status=True,
            order__order_date__date__gte=this_week_start
        ).annotate(
            order_num=Substr('order__oid', 2),  # Remove the '#' symbol (start from the second character)
            qty_sold=Sum('qty'),
            total_sold=Sum('total'),
            total_costing=Sum('cost'),
            order_date=F('order__order_date')  # Accessing the order_date field from CartOrder model
        ).values(
            'item',
            'order_num',  # This will contain the order number without the '#'
            'order_date',  # This will contain the order date
            'qty_sold',
            'total_sold',
            'total_cost'
        )
        

    if recurrent == "Monthly":
         # Monthly revenue
        revenue = CartOrder.objects.filter(
            paid_status=True,
            order_date__month=this_month,
            order_date__year=this_year
        ).aggregate(price=Sum("price"))["price"] or 0
        
        # 🔥 Monthly product sales Qty
        sales = CartOrderProducts.objects.filter(
            order__paid_status=True,
            order__order_date__month=this_month,
            order__order_date__year=this_year
        ).annotate(
            order_num=Substr('order__oid', 2),  # Remove the '#' symbol (start from the second character)
            qty_sold=Sum('qty'),
            total_sold=Sum('total'),
            total_costing=Sum('cost'),
            order_date=F('order__order_date')  # Accessing the order_date field from CartOrder model
        ).values(
            'item',
            'order_num',  # This will contain the order number without the '#'
            'order_date',  # This will contain the order date
            'qty_sold',
            'total_sold',
            'total_cost'
        )

    if recurrent == "Yearly":
        # Yearly revenue
        revenue = CartOrder.objects.filter(
            paid_status=True,
            order_date__year=this_year
        ).aggregate(price=Sum("price"))["price"] or 0
        
        # 🔥 Yearly product sales Qty
        sales = CartOrderProducts.objects.filter(
            order__paid_status=True,
            order__order_date__year=this_year
        ).annotate(
            order_num=Substr('order__oid', 2),  # Remove the '#' symbol (start from the second character)
            qty_sold=Sum('qty'),
            total_sold=Sum('total'),
            total_costing=Sum('cost'),
            order_date=F('order__order_date')  # Accessing the order_date field from CartOrder model
        ).values(
            'item',
            'order_num',  # This will contain the order number without the '#'
            'order_date',  # This will contain the order date
            'qty_sold',
            'total_sold',
            'total_cost'
        )

    total_orders_count = CartOrder.objects.count()
    all_products = Product.objects.all()
    all_categories = Category.objects.all()
    new_customers = User.objects.all().order_by("-id")[:6]
    latest_orders = CartOrder.objects.order_by("-id")[:10]

    context = {
        "user": user,
        "recurrent": recurrent,
        "total_revenue": total_revenue,
        "daily_revenue": daily_revenue,
        "revenue": revenue,
        "sales": sales,
        "all_products": all_products,
        "all_categories": all_categories,
        "new_customers": new_customers,
        "latest_orders": latest_orders,
        "total_orders_count": total_orders_count,
    }

    return render(request, "useradmin/generate-reports.html", context)

@user_passes_test(is_admin)
def products(request):
    all_products = Product.objects.all()
    all_categories = Category.objects.all()
    
    context = {
        "all_products": all_products,
        "all_categories": all_categories,
    }
    return render(request, "useradmin/products.html", context)

@user_passes_test(is_admin)
def add_product(request):
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            form.save_m2m()
            return redirect("useradmin:dashboard-products")
    else:
        form = AddProductForm()
    context = {
        'form':form
    }
    return render(request, "useradmin/add-products.html", context)

@user_passes_test(is_admin)
def edit_product(request, pid):
    product = Product.objects.get(pid=pid)  # Get product by ID
    tags = ProductTag.objects.all()  # Get all available tags

    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            tag_ids = request.POST.getlist('tags')  # Get list of selected tag IDs
            selected_tags = ProductTag.objects.filter(id__in=tag_ids)  # Fetch existing tag objects
            print(selected_tags) # Print
            form.tags = selected_tags
            new_product = form.save(commit=False)
            new_product.save()
            form.save_m2m()  # Save existing Many-to-Many relationships
            return redirect("useradmin:dashboard-products")

    else:
        form = AddProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'tags': tags,
    }
    return render(request, "useradmin/edit-products.html", context)

@user_passes_test(is_admin)
def delete_product(request, pid):
    product = Product.objects.get(pid=pid)
    product.delete()
    return redirect("useradmin:dashboard-products")

@user_passes_test(is_admin)
def orders(request):
    orders = CartOrder.objects.all()
    context = {
        'orders':orders,
    }
    return render(request, "useradmin/orders.html", context)

@user_passes_test(is_admin)
def order_detail(request, id):
    order = CartOrder.objects.get(id=id)
    order_items = CartOrderProducts.objects.filter(order=order)
    context = {
        'order':order,
        'order_items':order_items
    }
    return render(request, "useradmin/order_detail.html", context)

@user_passes_test(is_admin)
@csrf_exempt
def change_order_status(request, oid):
    order = CartOrder.objects.get(oid=oid)
    if request.method == "POST":
        status = request.POST.get("status")
        print("status =======", status)
        messages.success(request, f"Order status changed to {status}")
        order.product_status = status
        order.save()
    
    return redirect("useradmin:order_detail", order.id)

@user_passes_test(is_admin)
def shop_page(request):
    products = Product.objects.filter(user=request.user)
    revenue = CartOrder.objects.filter(paid_status=True).aggregate(price=Sum("price"))
    total_sales = CartOrderProducts.objects.filter(order__paid_status=True).aggregate(qty=Sum("qty"))

    context = {
        'products':products,
        'revenue':revenue,
        'total_sales':total_sales,
    }
    return render(request, "useradmin/shop_page.html", context)

@user_passes_test(is_admin)
def reviews(request):
    reviews = ProductReview.objects.all()
    context = {
        'reviews':reviews,
    }
    return render(request, "useradmin/reviews.html", context)

@user_passes_test(is_admin)
def settings(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        image = request.FILES.get("image")
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        bio = request.POST.get("bio")
        address = request.POST.get("address")
        country = request.POST.get("country")
        print("image ===========", image)
        
        if image != None:
            profile.image = image
        profile.full_name = full_name
        profile.phone = phone
        profile.bio = bio
        profile.address = address
        profile.country = country

        profile.save()
        messages.success(request, "Profile Updated Successfully")
        return redirect("useradmin:settings")
    
    context = {
        'profile':profile,
    }
    return render(request, "useradmin/settings.html", context)

@user_passes_test(is_admin)
def change_password(request):
    user = request.user

    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_new_password = request.POST.get("confirm_new_password")

        if confirm_new_password != new_password:
            messages.error(request, "Confirm Password and New Password Does Not Match")
            return redirect("useradmin:change_password")
        
        if check_password(old_password, user.password):
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password Changed Successfully")
            return redirect("useradmin:change_password")
        else:
            messages.error(request, "Old password is not correct")
            return redirect("useradmin:change_password")
    
    return render(request, "useradmin/change_password.html")
