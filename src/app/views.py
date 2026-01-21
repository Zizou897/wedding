import os
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

from .models import RSVP, Invitation

# Create your views here.



def home(request):
  
    template_name = "app/index.html"
    context = {}
    return render(request, template_name, context)


@csrf_exempt
def post_rsvp(request):
    url = ""
    is_true = True
    msg = "ce message est déjà envoyé"
    
    print("test")
    first_name = request.POST.get("first_name", "").strip()
    last_name = request.POST.get("last_name", "").strip()
    phone = request.POST.get("phone", "").strip()
    guests_count = int(request.POST.get("guests_count", 1))
    is_present = request.POST.get("is_present") == "true"
    message = request.POST.get("message", "").strip()

    # Sécurité minimale
    print("test2")
    invitation = Invitation.objects.first()  # Assuming only one invitation exists
    confirm, created = RSVP.objects.get_or_create(
        invitation=invitation,
        full_name=f"{first_name} {last_name}",
        phone=phone,
        guests_count=guests_count if is_present else 0,
        is_present=is_present,
        message=message
    )
    print("test3")
    if created:
        print("test4")
        if is_present:
            url = f"http://{request.get_host()}/GN/pass/{confirm.token}/"
            is_true = True
            msg = f"Merci pour votre confirmation de présence ! Nous avons hâte de vous voir."  
           
        else:
            is_true = False
            msg = "Nous sommes désolés que vous ne puissiez pas être des nôtres. Merci de nous avoir informés."
            
    data = {"success": is_true, "msg": msg, "url": url}
    print("URL du pass :", url)
    print("test5")
    return JsonResponse(data, safe=False)



def pass_view(request, token):
    # Cherche l'invité via son token
    rsvp = get_object_or_404(RSVP, token=token)

    # Si l'invité n'a pas confirmé sa présence, on peut griser le pass
    status_class = "present" if rsvp.is_present else "absent"

    context = {
        "rsvp": rsvp,
        "status_class": status_class,
        "invitation": {
            "couple_name": "gio & Nadège",
            "event_date": "28 Janvier 2026",
            "event_location": "Abidjan, Plateau",
        }
    }
    return render(request, "app/pass_detail.html", context)




def pass_pdf(request, token):
    rsvp = get_object_or_404(RSVP, token=token)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Pass_{rsvp.full_name}.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # 🎨 FOND
    c.setFillColorRGB(0.97, 0.95, 0.92)
    c.rect(0, 0, width, height, fill=1)

    # 💍 TITRE
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 3*cm, "Joefrey & Sheila")

    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 4.2*cm, "Invitation officielle")

    # 📋 INFOS INVITÉ
    c.setFont("Helvetica-Bold", 16)
    c.drawString(4*cm, height - 6.5*cm, "Invité :")
    c.setFont("Helvetica", 16)
    c.drawString(8*cm, height - 6.5*cm, rsvp.full_name)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(4*cm, height - 8*cm, "Nombre de personnes :")
    c.setFont("Helvetica", 14)
    c.drawString(10.5*cm, height - 8*cm, str(rsvp.guests_count))

    c.drawString(4*cm, height - 9.5*cm, "Table :")
    c.drawString(8*cm, height - 9.5*cm, f"Table {getattr(rsvp, 'table_number', '-')}")


    # 📅 INFOS MARIAGE
    c.setFont("Helvetica-Bold", 14)
    c.drawString(4*cm, height - 11.5*cm, "Date :")
    c.drawString(8*cm, height - 11.5*cm, "28 Janvier 2026")

    c.drawString(4*cm, height - 13*cm, "Lieu :")
    c.drawString(8*cm, height - 13*cm, "Abidjan, Plateau")

    # 📌 QR CODE
    if rsvp.qr_code:
        qr_path = rsvp.qr_code.path
        c.drawImage(qr_path, width/2 - 3*cm, height - 20*cm, 6*cm, 6*cm)

    # 💬 MESSAGE
    if rsvp.message:
        c.setFont("Helvetica-Oblique", 11)
        c.drawCentredString(width / 2, height - 22.5*cm, f"“{rsvp.message}”")

    # 🧾 STATUT
    c.setFont("Helvetica-Bold", 13)
    status = "PRÉSENCE CONFIRMÉE" if rsvp.is_present else "ABSENCE ENREGISTRÉE"
    c.drawCentredString(width / 2, height - 25*cm, status)

    # 🎉 FOOTER
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, 2*cm, "Merci de présenter ce pass à l’entrée")

    c.showPage()
    c.save()

    return response



def scan_pass(request, token):
    try:
        rsvp = RSVP.objects.get(token=token)
    except RSVP.DoesNotExist:
        return render(request, "app/validation/scan_invalid.html", )

    # ❌ Invité absent
    if not rsvp.is_present:
        return render(request, "app/validation/scan_invalid.html", {
            "message": "Invité non confirmé"
        })

    # ⚠️ Déjà scanné
    if rsvp.is_checked_in:
        return render(request, "app/validation/scan_already.html", {
            "rsvp": rsvp
        })

    # ✅ Validation
    rsvp.is_checked_in = True
    rsvp.checked_in_at = timezone.now()
    rsvp.save()

    return render(request, "app/validation/scan_success.html", {
        "rsvp": rsvp
    })