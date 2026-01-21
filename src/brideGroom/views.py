import openpyxl
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login 
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

# Create your views here.

from app.models import Invitation, RSVP


def login(request):
    
    if request.method == "POST":
        password = request.POST.get("password")
        
        if password == "admin123":
            request.session['is_logged_in'] = True
            return redirect("brideGroom:transition")  
        else:
            messages.error(request, "Invalid password. Please try again.")  
        print(password)
    
    
    template_name = "dashboard/login.html"
    context = {}
    return render(request, template_name, context)


def logout(request):
	request.session.flush()
	return redirect('brideGroom:index')


def transition(request):
    if not request.session.get('is_logged_in'):
        return redirect("brideGroom:index")
    
    template_name = "dashboard/transition.html"
    context = {}
    return render(request, template_name, context)


def dashboard(request):
    
    if not request.session.get('is_logged_in'):
        return redirect("brideGroom:index")

    invitations = Invitation.objects.first()
    rsvps = RSVP.objects.filter(invitation=invitations)
    
    presents = rsvps.filter(is_present=True)
    absents = rsvps.filter(is_present=False)
    
    stats = {
    "total_rsvps": rsvps.count(),
    "total_presents": presents.count(),
    "total_absents": absents.count()
    }

    template_name = "dashboard/dashboard.html"
    context = {
        "stats": stats,
        "invitations": invitations,
        "rsvps": rsvps
        
    }
    return render(request, template_name, context)



def export_rsvps_excel(request):
    invitation = Invitation.objects.first()  # adapter selon votre logique
    rsvps = RSVP.objects.filter(invitation=invitation)

    # Créer un workbook Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Invités"

    # En-têtes
    headers = ["Nom complet", "Téléphone", "Nombre d'invités", "Présence", "Message"]
    ws.append(headers)

    # Données
    for rsvp in rsvps:
        ws.append([
            rsvp.full_name,
            rsvp.phone,
            rsvp.guests_count,
            "Oui" if rsvp.is_present else "Non",
            rsvp.message or ""
        ])

    # Réponse HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=liste_invites.xlsx'
    wb.save(response)
    return response




def export_rsvps_pdf(request):
    invitation = Invitation.objects.first()
    rsvps = RSVP.objects.filter(invitation=invitation)

    template_path = 'pdf_template/rsvp_pdf.html'
    context = {'rsvps': rsvps, 'invitation': invitation}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_invites.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF')
    return response




def dashboard_live(request):
    if not request.session.get('is_logged_in'):
        return redirect("brideGroom:index")
    
    template_name = "dashboard/dashboard_live.html"
    context = {}
    return render(request, template_name, context)



def dashboard_live_data(request):
    if not request.session.get('is_logged_in'):
        return redirect("brideGroom:index")
    
    
    total = RSVP.objects.filter(is_present=True).count()
    arrived = RSVP.objects.filter(is_checked_in=True).count()
    pending = total - arrived
    
    arrived_list = RSVP.objects.filter(is_checked_in=True).order_by('-checked_in_at')[:20]
    
    data = {
        "total": total,
        "arrived": arrived,
        "pending": pending,
        "arrivals": [
            {
                "name": r.full_name,
                "guests": r.guests_count,
                "time": r.checked_in_at.strftime("%H:%M:%S")
            }
            for r in arrived_list
        ]
    }

    return JsonResponse(data)