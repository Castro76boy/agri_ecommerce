from decimal import Decimal
import socket
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError

def format_fcfa(amount):
    """Formate un montant en FCFA avec séparateur de milliers"""
    if amount is None:
        return "0 FCFA"
    return "{:,.0f} FCFA".format(float(amount)).replace(",", " ")

def validate_email_with_domain(email):
    """Valide le format de l'email et vérifie le domaine"""
    try:
        # Validation de base du format
        django_validate_email(email)
        
        # Vérification du domaine
        domain = email.split('@')[1]
        try:
            socket.gethostbyname(domain)
        except socket.gaierror:
            raise ValidationError(f"Le domaine {domain} semble invalide")
            
    except ValidationError as e:
        raise ValidationError(f"Email invalide: {str(e)}")
