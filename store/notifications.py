from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging
from .utils import format_fcfa

logger = logging.getLogger(__name__)

def send_order_confirmation_email(order):
    """
    Envoie un email de confirmation de commande au client
    """
    try:
        # Contexte pour le template
        context = {
            'order': order,
            'user': order.user,
            'items': order.items.all(),
        }
        
        # Rendre le template HTML
        html_message = render_to_string('store/emails/order_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        # Envoyer l'email
        send_mail(
            subject=f'Confirmation de votre commande #{order.id}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email de confirmation envoyé pour la commande #{order.id}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email de confirmation: {str(e)}")
        return False

def send_order_confirmation_sms(order):
    """
    Envoie un SMS de confirmation de commande au client
    """
    try:
        # Vérifier si la configuration Twilio est complète
        if not all([
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
            settings.TWILIO_PHONE_NUMBER
        ]):
            logger.error("Configuration Twilio incomplète")
            return False
            
        # Créer le client Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Préparer le message
        message = f"""
        Confirmation de commande #{order.id}
        Montant total: {order.get_total_amount_fcfa()}
        Livraison à: {order.address}
        
        Merci pour votre commande!
        """
        
        # Envoyer le SMS
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=order.phone
        )
        logger.info(f"SMS de confirmation envoyé pour la commande #{order.id}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du SMS de confirmation: {str(e)}")
        return False
