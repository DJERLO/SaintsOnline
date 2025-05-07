# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import CartOrder

@receiver(post_save, sender=CartOrder)
def send_order_status_email(sender, instance, created, **kwargs):
    """
    This signal is triggered after an Order is saved(Created) or changes(Update). It will send an email 
    to the customer if the order status is updated.
    """

    """STATUS
    ("processing", "Processing"),
    ("packaging", "Packing"),
    ("Ready To Pickup", "Ready To Pickup"),
    ("All Ready Pickup", "Has been Pickup"),
    """
    # If the order status is changed (not created), send an email
    if not created:  # Means the order was updated, not created
     subject = f"Update on Your Order #{instance.oid}"
     message = (
        f"Dear {instance.full_name},\n\n"
        f"We would like to inform you that the status of your order (Order ID: {instance.oid}) has been updated.\n\n"
        f"**Current Status:** {instance.product_status}\n\n"
        f"If you have any questions or need further assistance, feel free to contact our support team.\n\n"
        f"Thank you for shopping with us.\n\n"
        f"Best regards,\n"
        f"Saint Clare Online Shop Team"
    )
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [instance.email]

    send_mail(subject, message, from_email, recipient_list)
