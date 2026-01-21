import uuid
from django.utils import timezone
from django.db import models
from django.core.files import File
import qrcode
from io import BytesIO

# Create your models here.


class Convention(models.Model):
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    publish = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Invitation(Convention):
    couple_name = models.CharField(max_length=255)
    wedding_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    map_link = models.URLField()
    description = models.TextField()
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Les Mariés"
        verbose_name_plural = "Les Mariés"

    def __str__(self):
        return self.couple_name
    


class RSVP(Convention):
    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    guests_count = models.PositiveIntegerField()
    is_present = models.BooleanField(default=True)
    message = models.TextField(blank=True, null=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    # 🔐 NOUVEAUX CHAMPS
    is_checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "RSVP"
        verbose_name_plural = "RSVPs"  
         
    def __str__(self):
        return f"RSVP de {self.full_name} pour {self.invitation.couple_name}"
    
    
    def generate_qr(self):
        # Créer le QR code pour l’URL du pass
        qr_url = f"https://9805c80101fd.ngrok-free.app/GN/scan/{self.token}/"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Sauvegarde dans ImageField
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        filename = f'qr_{self.pk}.png'
        self.qr_code.save(filename, File(buffer), save=False)
        buffer.close()
