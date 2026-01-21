from django.urls import path
from .views import home, post_rsvp, pass_view, pass_pdf, scan_pass

urlpatterns = [
    path("GN/", home, name="home"),
    path("post_rsvp/", post_rsvp, name="post_rsvp"),
    path('GN/pass/<uuid:token>/', pass_view, name='pass_view'),
    path('GN/pass/<uuid:token>/pdf/', pass_pdf, name='pass_pdf'),
    path('GN/scan/<uuid:token>/', scan_pass, name='scan_pass'),

]
