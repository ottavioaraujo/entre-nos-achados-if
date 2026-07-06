from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import CampusItem, CampusItemComment


class CampusItemForm(forms.ModelForm):
    event_period = forms.ChoiceField(
        label="Quando aconteceu?",
        choices=CampusItem.EventPeriod.choices,
        initial=CampusItem.EventPeriod.TODAY,
        widget=forms.Select(),
    )
    photo_upload = forms.ImageField(
        label="Foto do objeto",
        required=False,
        widget=forms.ClearableFileInput(attrs={"accept": "image/*"}),
    )

    class Meta:
        model = CampusItem
        fields = ["kind", "name", "category", "event_period", "location", "description", "contact_phone"]
        widgets = {
            "kind": forms.HiddenInput(),
            "description": forms.Textarea(attrs={"rows": 3}),
            "contact_phone": forms.TelInput(attrs={"placeholder": "(11) 99999-9999", "inputmode": "tel"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if self.instance.event_period:
                self.initial["event_period"] = self.instance.event_period
            else:
                recorded_date = self.instance.event_date.strftime("%d/%m/%Y")
                self.fields["event_period"].choices = [
                    ("keep", f"Manter data atual ({recorded_date})"),
                    *CampusItem.EventPeriod.choices,
                ]
                self.initial["event_period"] = "keep"

    def clean_event_period(self):
        value = self.cleaned_data["event_period"]
        allowed = {choice for choice, _label in CampusItem.EventPeriod.choices}
        if value == "keep" and self.instance.pk and not self.instance.event_period:
            return value
        if value not in allowed:
            raise forms.ValidationError("Escolha Hoje ou Nesta semana.")
        return value

    def clean_photo_upload(self):
        photo = self.cleaned_data.get("photo_upload")
        if photo and photo.size > 4 * 1024 * 1024:
            raise forms.ValidationError("A foto deve ter no máximo 4 MB após a otimização.")
        if photo:
            image = getattr(photo, "image", None)
            if getattr(image, "format", "") not in {"JPEG", "PNG", "GIF", "WEBP"}:
                raise forms.ValidationError("Use uma imagem JPG, PNG, GIF ou WebP.")
        return photo

    def save(self, commit=True):
        item = super().save(commit=False)
        period = self.cleaned_data["event_period"]
        if period == "keep":
            item.event_period = None
        else:
            item.event_period = period
            today = timezone.localdate()
            item.event_date = today if period == CampusItem.EventPeriod.TODAY else today - timedelta(days=today.weekday())
        if commit:
            item.save()
            self.save_m2m()
        return item

    def clean_contact_phone(self):
        phone = self.cleaned_data.get("contact_phone", "")
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) in (10, 11):
            digits = "55" + digits
        if not 12 <= len(digits) <= 15:
            raise forms.ValidationError("Informe o número com DDD. Ex.: (11) 99999-9999.")
        return "+" + digits


class CampusItemCommentForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    class Meta:
        model = CampusItemComment
        fields = ["author", "body"]
        widgets = {
            "author": forms.TextInput(attrs={"maxlength": 60, "autocomplete": "name"}),
            "body": forms.Textarea(attrs={"rows": 2, "maxlength": 500}),
        }

    def clean_website(self):
        value = self.cleaned_data.get("website", "")
        if value:
            raise forms.ValidationError("Não foi possível enviar este comentário.")
        return value
