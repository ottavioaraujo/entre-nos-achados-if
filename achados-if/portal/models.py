import re
from urllib.parse import quote

from django.core.exceptions import ValidationError
from django.db import models


class CampusItem(models.Model):
    class Kind(models.TextChoices):
        LOST = "lost", "Perdido"
        FOUND = "found", "Encontrado"

    class Category(models.TextChoices):
        ELECTRONICS = "eletronicos", "Eletrônicos"
        SCHOOL = "material_escolar", "Material escolar"
        CLOTHING = "roupas_acessorios", "Roupas e acessórios"
        KEYS_DOCS = "chaves_documentos", "Chaves e documentos"
        OTHER = "outros", "Outros"

    kind = models.CharField("tipo do aviso", max_length=8, choices=Kind.choices, db_index=True)
    name = models.CharField("nome do item", max_length=70)
    category = models.CharField("categoria", max_length=24, choices=Category.choices, db_index=True)
    event_date = models.DateField("data aproximada")
    location = models.CharField("local no campus", max_length=80)
    description = models.CharField("descrição", max_length=300)
    contact_phone = models.CharField("WhatsApp de contato", max_length=20)
    photo = models.ImageField("foto", upload_to="items/%Y/%m/", blank=True)
    reporter = models.BigIntegerField("publicado por", db_column="reporter_id", null=True, blank=True)
    is_resolved = models.BooleanField("resolvido", default=False, db_index=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "item"
        verbose_name_plural = "itens"

    def __str__(self):
        return f"{self.get_kind_display()}: {self.name}"

    def clean(self):
        digits = re.sub(r"\D", "", self.contact_phone or "")
        if len(digits) in (10, 11):
            digits = "55" + digits
        if not 12 <= len(digits) <= 15:
            raise ValidationError({"contact_phone": "Informe um telefone válido com DDD e código do país."})
        self.contact_phone = "+" + digits

    @property
    def whatsapp_url(self):
        digits = re.sub(r"\D", "", self.contact_phone)
        if len(digits) in (10, 11):
            digits = "55" + digits
        if not 12 <= len(digits) <= 15:
            return ""
        if self.kind == self.Kind.LOST:
            message = f"Olá! Vi seu aviso no Entre Nós sobre o item perdido ‘{self.name}’. Tenho uma informação que pode ajudar. Podemos conversar?"
        else:
            message = f"Olá! Vi seu aviso no Entre Nós sobre ‘{self.name}’, encontrado em {self.location}. Acredito que possa ser meu/de alguém que conheço. Podemos confirmar alguns detalhes?"
        return f"https://wa.me/{digits}?text={quote(message)}"
