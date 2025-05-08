# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import CartOrder

@receiver(post_save, sender=CartOrder)
def send_order_status_email(sender, instance, created, **kwargs):
    """
    This signal is triggered after a CartOrder is saved.
    It sends an email to the customer if the order status is updated.
    """

    # Only send email if the order is updated, not when first created
    if not created:
        subject = f"Update on Your Order #{instance.oid}"
        message = (
            f"Dear {instance.full_name},\n\n"
            f"We would like to inform you that the status of your order (Order ID: {instance.oid}) has been updated.\n\n"
            f"**Current Status:** {instance.product_status}\n\n"
            f"If you have any questions or need further assistance, feel free to contact our support team.\n\n"
            f"Thank you for shopping with us.\n\n"
            f"Best regards,\n"
            f"Saint Clare Online Shop Team.\n\n"
            f"**Note:** This is an automated message. Please do not reply directly to this email.\n"
        )
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [instance.email]

        send_mail(subject, message, from_email, recipient_list)
