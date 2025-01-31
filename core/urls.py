from django.urls import path, include
from core.views import index
from core.views import create_checkout_session, customer_dashboard, save_checkout_info, category_list_view, checkout, product_list_view, category_product_list_view, cart_view, vendor_list_view, vendor_detail_view, product_detail_view, tag_list, ajax_add_review, search_view, filter_products,  add_to_cart, delete_item_from_cart, update_cart, order_detail, payment_completed_view, payment_failed_view, make_address_default, contact, ajax_contact_form, purchase_guide, privacy_policy, terms_of_service


app_name = "core"

urlpatterns = [

    # Homepage 
    path("", index, name="index"),
    path("products/", product_list_view, name="product-list"),
    path("product/<pid>/", product_detail_view, name="product-detail"),

    # Category
    path("category/", category_list_view, name="category-list"),
    path("category/<cid>/", category_product_list_view, name="category-product-list"),

    # Vendor
    path("vendors/", vendor_list_view, name="vendor-list"),
    path("vendor/<vid>/", vendor_detail_view, name="vendor-detail"),

    #Tags
    path("products/tag/<slug:tag_slug>/", tag_list, name="tags"),

    # Add Reviews
    path("ajx-add-review/<int:pid>", ajax_add_review, name="ajax-add-review"), 

    # Search
    path("search/", search_view, name="search"),

    # Filter 
    path("filter-products/", filter_products, name="filter-products"),

    # Add to cart
    path("add-to-cart/", add_to_cart, name="add-to-cart"),

    # Cart Page URL
    path("cart/", cart_view, name="cart"),

    # Delete ITem from Cart
    path("delete-from-cart/", delete_item_from_cart, name="delete-from-cart"),

    # Update  Cart
    path("update-cart/", update_cart, name="update-cart"),

    # Checkout  URL
    path("checkout/<oid>/", checkout, name="checkout"),

    # Paypal URL
    path('paypal/', include('paypal.standard.ipn.urls')),

    # Payment Successful
    path("payment-completed/<oid>/", payment_completed_view, name="payment-completed"),

    # Payment Failed
    path("payment-failed/", payment_failed_view, name="payment-failed"),

    # Dahboard URL
    path("dashboard/", customer_dashboard, name="dashboard"),

    # Order Detail URL
    path("dashboard/order/<int:id>", order_detail, name="order-detail"),

    # Making address defaulyS
    path("make-default-address/", make_address_default, name="make-default-address"),

    path("contact/", contact, name="contact"),
    path("ajax-contact-form/", ajax_contact_form, name="ajax-contact-form"),

    # New Routes
    path("save_checkout_info/", save_checkout_info, name="save_checkout_info"),
    path("api/create_checkout_session/<oid>/", create_checkout_session, name="api_checkout_session"),

    # Purchase Guide
    path("purchase_guide/", purchase_guide, name="purchase_guide"),

    # Privacy Policy Guide 
    path("privacy_policy/", privacy_policy, name="privacy_policy"),

    # Terms And Conditions Guide
    path("terms_of_service/", terms_of_service, name="terms_of_service")
]