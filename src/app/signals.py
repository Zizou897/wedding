from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RSVP


@receiver(post_save, sender=RSVP)
def generate_qr_code(sender, instance, created, **kwargs): 
    if created and not instance.qr_code:
        # Générer le QR code
        instance.generate_qr()
        instance.save()