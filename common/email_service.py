from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from order_management.models import Order


def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer
    """
    try:
        subject = f"Order Confirmation - {order.order_number}"
        context = {
            "order": order,
            "customer": order.customer,
            "items": order.items.all(),
            "total_amount": order.total_amount,
        }
        html_message = render_to_string("emails/order_confirmation.html", context)
        plain_message = f"""
        Thank you for your order!
        
        Order Number: {order.order_number}
        Total Amount: ${order.total_amount}
        
        Your order has been received and is being processed.
        """
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order confirmation email: {str(e)}")
        return False


def send_payment_confirmation_email(order):
    """
    Send payment confirmation email to customer
    """
    try:
        subject = f"Payment Confirmed - Order {order.order_number}"
        context = {
            "order": order,
            "customer": order.customer,
            "items": order.items.all(),
            "total_amount": order.total_amount,
            "crm_sync_status": order.crm_sync_status,
        }
        html_message = render_to_string("emails/payment_confirmation.html", context)
        plain_message = f"""
        Payment Confirmed!
        
        Order Number: {order.order_number}
        Amount Paid: ${order.total_amount}
        Status: {order.crm_sync_status or 'N/A'}
        
        Thank you for your purchase!
        """
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending payment confirmation email: {str(e)}")
        return False


def send_order_status_update_email(order, old_status=None):
    """
    Send order status update email to customer
    """
    try:
        subject = f"Order Status Update - {order.order_number}"
        context = {
            "order": order,
            "customer": order.customer,
            "old_status": old_status,
            "new_status": order.status,
            "items": order.items.all(),
            "total_amount": order.total_amount,
        }
        html_message = render_to_string("emails/order_status_update.html", context)
        plain_message = f"""
        Order Status Update
        
        Order Number: {order.order_number}
        Previous Status: {old_status or 'N/A'}
        New Status: {order.status}
        
        Your order status has been updated.
        """
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order status update email: {str(e)}")
        return False


