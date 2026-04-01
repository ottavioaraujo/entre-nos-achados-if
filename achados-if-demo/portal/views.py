from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from .forms import CampusItemForm
from .models import CampusItem


def index(request):
    """Public landing page; browsing and item submission live on the board."""
    totals = CampusItem.objects.filter(is_resolved=False).aggregate(
        total=Count("id"),
        lost=Count("id", filter=Q(kind=CampusItem.Kind.LOST)),
        found=Count("id", filter=Q(kind=CampusItem.Kind.FOUND)),
    )
    return render(request, "portal/landing.html", {
        "totals": totals,
        "form": CampusItemForm(initial={"kind": CampusItem.Kind.LOST}),
        "demo_login_enabled": settings.DEBUG,
    })


def board(request):
    """Public item board, separate from the landing page."""
    items = CampusItem.objects.filter(is_resolved=False)
    kind = request.GET.get("tipo", "all")
    category = request.GET.get("categoria", "")
    query = request.GET.get("q", "").strip()
    if kind in {CampusItem.Kind.LOST, CampusItem.Kind.FOUND}:
        items = items.filter(kind=kind)
    if category in CampusItem.Category.values:
        items = items.filter(category=category)
    if query:
        items = items.filter(
            Q(name__icontains=query)
            | Q(location__icontains=query)
            | Q(description__icontains=query)
        )

    totals = CampusItem.objects.filter(is_resolved=False).aggregate(
        total=Count("id"),
        lost=Count("id", filter=Q(kind=CampusItem.Kind.LOST)),
        found=Count("id", filter=Q(kind=CampusItem.Kind.FOUND)),
    )

    return render(request, "portal/board.html", {
        "items": items,
        "totals": totals,
        "form": CampusItemForm(initial={"kind": request.GET.get("tipo", CampusItem.Kind.LOST)}),
        "demo_login_enabled": settings.DEBUG,
        "kind_filter": kind,
        "category_filter": category,
        "query": query,
        "category_choices": CampusItem.Category.choices,
    })


@require_POST
def publish_item(request):
    """Publish a lost/found notice with or without a demo account."""
    form = CampusItemForm(request.POST, request.FILES)
    wants_json = request.headers.get("x-requested-with") == "XMLHttpRequest"
    if form.is_valid():
        item = form.save(commit=False)
        item.reporter = request.user if request.user.is_authenticated else None
        item.save()
        if wants_json:
            return JsonResponse({
                "ok": True,
                "message": "Aviso publicado no mural do campus.",
                "redirect": reverse("portal:board"),
            })
        messages.success(request, "Aviso publicado no mural do campus.")
        return redirect("portal:board")

    if wants_json:
        errors = {name: [str(error) for error in values] for name, values in form.errors.items()}
        return JsonResponse({
            "ok": False,
            "message": "Confira os campos destacados e tente novamente.",
            "errors": errors,
        }, status=422)
    messages.error(request, "Confira os dados do aviso e tente novamente.")
    return redirect("portal:board")


@require_http_methods(["GET", "POST"])
def demo_login(request):
    """Local-only demo credentials; never expose this route outside DEBUG."""
    if not settings.DEBUG:
        raise Http404

    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip().lower()
        password = request.POST.get("password", "")
        if username in {"admin", "user"}:
            User = get_user_model()
            is_admin = username == "admin"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": "Admin de teste" if is_admin else "Usuário de teste",
                    "is_staff": is_admin,
                },
            )
            if created:
                user.set_password("1234")
                user.save(update_fields=["password"])
            user.is_staff = is_admin
            user.is_superuser = False
            user.set_password("1234")
            user.save(update_fields=["is_staff", "is_superuser", "password"])
            authenticated_user = authenticate(request, username=username, password=password)
            if authenticated_user:
                login(request, authenticated_user, backend="django.contrib.auth.backends.ModelBackend")
                return redirect("portal:management" if is_admin else "portal:account")
        error = "Confira o usuário e a senha de demonstração."
    return render(request, "portal/demo_login.html", {"error": error})
@login_required
def account(request):
    return render(request, "portal/account.html", {
        "form": CampusItemForm(initial={"kind": CampusItem.Kind.LOST}),
        "demo_login_enabled": settings.DEBUG,
        "items": request.user.campus_items.all(),
    })


@user_passes_test(lambda user: user.is_staff)
def management(request):
    items = CampusItem.objects.select_related("reporter").all()
    status = request.GET.get("status", "active")
    kind = request.GET.get("tipo", "all")
    query = request.GET.get("q", "").strip()
    if status == "active":
        items = items.filter(is_resolved=False)
    elif status == "resolved":
        items = items.filter(is_resolved=True)
    if kind in {CampusItem.Kind.LOST, CampusItem.Kind.FOUND}:
        items = items.filter(kind=kind)
    if query:
        items = items.filter(
            Q(name__icontains=query)
            | Q(location__icontains=query)
            | Q(description__icontains=query)
            | Q(contact_phone__icontains=query)
        )

    totals = CampusItem.objects.aggregate(
        total=Count("id"),
        lost=Count("id", filter=Q(kind=CampusItem.Kind.LOST)),
        found=Count("id", filter=Q(kind=CampusItem.Kind.FOUND)),
        resolved=Count("id", filter=Q(is_resolved=True)),
    )
    return render(request, "portal/management.html", {
        "items": items,
        "totals": totals,
        "status_filter": status,
        "kind_filter": kind,
        "query": query,
    })


@user_passes_test(lambda user: user.is_staff)
def edit_item(request, pk):
    item = get_object_or_404(CampusItem, pk=pk)
    form = CampusItemForm(instance=item)
    if request.method == "POST":
        form = CampusItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Aviso atualizado.")
            return redirect("portal:management")
    return render(request, "portal/item_edit.html", {"item": item, "form": form})


@require_POST
@user_passes_test(lambda user: user.is_staff)
def toggle_resolution(request, pk):
    item = get_object_or_404(CampusItem, pk=pk)
    item.is_resolved = not item.is_resolved
    item.save(update_fields=["is_resolved"])
    messages.success(request, "Status do aviso atualizado.")
    return redirect("portal:management")


@require_POST
@user_passes_test(lambda user: user.is_staff)
def delete_item(request, pk):
    item = get_object_or_404(CampusItem, pk=pk)
    photo_name = item.photo.name if item.photo else ""
    item.delete()
    if photo_name:
        default_storage.delete(photo_name)
    messages.success(request, "Aviso removido do mural.")
    return redirect("portal:management")


@require_POST
@login_required
def sign_out(request):
    logout(request)
    messages.success(request, "Você saiu da conta de demonstração.")
    return redirect("portal:index")
