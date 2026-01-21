from django import forms
from .models import RSVP

class RSVPForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()

    class Meta:
        model = RSVP
        fields = ["phone", "guests_count", "is_present", "message"]

    def clean_is_present(self):
        return self.cleaned_data["is_present"] == "true"
