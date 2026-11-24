from datetime import date, timedelta
from pathlib import Path
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from portal.models import CampusItem


class Command(BaseCommand):
    help = "Cria as contas e os avisos iniciais do ambiente de demonstração."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("setup_demo só pode ser executado com DEBUG=True.")

        User = get_user_model()
        for username, first_name, is_staff in (
            ("admin", "Admin de demonstração", True),
            ("user", "Usuário de demonstração", False),
        ):
            user, _ = User.objects.get_or_create(username=username)
            user.first_name = first_name
            user.is_staff = is_staff
            user.is_superuser = False
            user.is_active = True
            user.set_password("1234")
            user.save()

        photo_names = (
            "boneco-de-pano.jpg",
            "anel-prateado.jpg",
            "garrafa-lilas.jpg",
        )
        source_dir = Path(__file__).resolve().parents[2] / "static" / "portal" / "demo-items"
        target_dir = settings.MEDIA_ROOT / "items" / "demo"
        target_dir.mkdir(parents=True, exist_ok=True)
        for photo_name in photo_names:
            source = source_dir / photo_name
            if not source.is_file():
                raise CommandError(f"Foto de demonstração não encontrada: {source}")
            shutil.copy2(source, target_dir / photo_name)

        examples = [
            (CampusItem.Kind.FOUND, "Anel prateado", CampusItem.Category.OTHER,
             1, "Perto do bloco de salas", "Anel liso prateado. Detalhes únicos serão confirmados com o dono.",
             "anel-prateado.jpg", "Chaveiro com duas chaves"),
            (CampusItem.Kind.LOST, "Boneco de pano", CampusItem.Category.OTHER,
             2, "Biblioteca", "Boneco artesanal de tecido com roupa branca e azul; a foto também mostra um estojo cinza e um lápis verde.",
             "boneco-de-pano.jpg", "Estojo azul"),
            (CampusItem.Kind.FOUND, "Garrafa lilás", CampusItem.Category.OTHER,
             3, "Banheiro do bloco B", "Garrafa plástica lilás encontrada perto da pia.",
             "garrafa-lilas.jpg", "Garrafa térmica"),
            (CampusItem.Kind.LOST, "Fone de ouvido", CampusItem.Category.ELECTRONICS,
             4, "Laboratório de informática", "Fone sem fio em estojo escuro.", None, None),
            (CampusItem.Kind.LOST, "Caderno de capa preta", CampusItem.Category.SCHOOL,
             6, "Bloco de aulas", "Caderno universitário com anotações de matemática.", None, None),
        ]

        for kind, name, category, days_ago, location, description, photo_name, legacy_name in examples:
            names = [name] + ([legacy_name] if legacy_name else [])
            item = CampusItem.objects.filter(
                kind=kind,
                name__in=names,
                contact_phone="+5500000000000",
                reporter__isnull=True,
            ).order_by("id").first()
            if item is None:
                item = CampusItem(kind=kind, contact_phone="+5500000000000", reporter=None)

            item.name = name
            item.category = category
            item.event_date = date.today() - timedelta(days=days_ago)
            item.location = location
            item.description = description
            item.photo = f"items/demo/{photo_name}" if photo_name else ""
            item.is_resolved = False
            item.save()

        self.stdout.write(self.style.SUCCESS("Contas de demonstração e 6 avisos prontos."))
