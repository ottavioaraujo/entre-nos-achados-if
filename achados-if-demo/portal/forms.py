from django import forms

from .models import CampusItem


class CampusItemForm(forms.ModelForm):
    class Meta:
        model = CampusItem
        fields = ["kind", "name", "category", "event_date", "location", "description", "contact_phone", "photo"]
        widgets = {
            "kind": forms.HiddenInput(),
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "contact_phone": forms.TelInput(attrs={"placeholder": "(11) 99999-9999", "inputmode": "tel"}),
            "photo": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("A foto deve ter no máximo 5 MB.")
        return photo

    def clean_contact_phone(self):
        phone = self.cleaned_data.get("contact_phone", "")
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) in (10, 11):
            digits = "55" + digits
        if not 12 <= len(digits) <= 15:
            raise forms.ValidationError("Informe o número com DDD. Ex.: (11) 99999-9999.")
        return "+" + digits
