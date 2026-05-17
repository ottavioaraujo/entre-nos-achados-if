import json
import logging
import re
import secrets
from base64 import b64encode
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage
from django.db.models import Count, Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CampusItemForm
from .models import CampusItem


logger = logging.getLogger(__name__)


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
        "demo_login_enabled": False,
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
        "demo_login_enabled": False,
        "kind_filter": kind,
        "category_filter": category,
        "query": query,
        "category_choices": CampusItem.Category.choices,
    })


@require_POST
def publish_item(request):
    """Publish a lost/found notice with or without an authenticated account."""
    form = CampusItemForm(request.POST, request.FILES)
    wants_json = request.headers.get("x-requested-with") == "XMLHttpRequest"
    if form.is_valid():
        item = form.save(commit=False)
        item.reporter = request.user.pk if request.user.is_authenticated else None
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


def suap_login(request):
    if not (settings.SUAP_BASE_URL and settings.SUAP_CLIENT_ID and settings.SUAP_CLIENT_SECRET):
        return render(request, "portal/login.html", {"suap_configured": False})

    state = secrets.token_urlsafe(32)
    # Keep each authorization attempt separate so parallel login tabs do not
    # overwrite one another's CSRF state in the shared browser session.
    request.session[f"suap_oauth_state:{state}"] = state
    requested_next = request.GET.get("next", "")
    request.session[f"suap_oauth_next:{state}"] = requested_next if url_has_allowed_host_and_scheme(
        requested_next,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ) else ""

    params = urlencode({
        "response_type": "code",
        "client_id": settings.SUAP_CLIENT_ID,
        "redirect_uri": settings.SUAP_REDIRECT_URI,
        "state": state,
    })
    return redirect(f"{settings.SUAP_BASE_URL}/o/authorize/?{params}")


def suap_callback(request):
    if request.GET.get("error"):
        messages.error(request, "O acesso pelo SUAP foi cancelado ou recusado.")
        return redirect("portal:index")

    received_state = request.GET.get("state", "")
    expected_state = request.session.pop(f"suap_oauth_state:{received_state}", "")
    if not expected_state or not secrets.compare_digest(expected_state, received_state):
        return HttpResponseBadRequest("Não foi possível validar o retorno do SUAP. Inicie o login novamente.")

    code = request.GET.get("code", "")
    if not code:
        messages.error(request, "O SUAP não retornou um código de autorização.")
        return redirect("portal:index")

    oauth_stage = "token exchange"
    try:
        token_data = _post_suap_form("/o/token/", {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SUAP_REDIRECT_URI,
        }, authenticate_client=True)
        access_token = token_data.get("access_token", "")
        if not access_token:
            raise ValueError("O SUAP não retornou um token de acesso.")
        oauth_stage = "profile lookup"
        profile = _get_suap_profile(access_token, token_data.get("scope", ""))
    except HTTPError as exc:
        # Keep OAuth codes, access tokens, secrets, and response bodies out of logs.
        try:
            error_name = json.loads(exc.read()).get("error", "unknown")
        except (ValueError, AttributeError):
            error_name = "unknown"
        if not isinstance(error_name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", error_name):
            error_name = "unknown"
        logger.warning("SUAP OAuth %s failed with HTTP status %s (%s)", oauth_stage, exc.code, error_name)
        messages.error(request, "Não foi possível validar sua conta no SUAP. Tente novamente.")
        return redirect("portal:index")
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        logger.warning("SUAP OAuth %s failed (%s)", oauth_stage, type(exc).__name__)
        messages.error(request, "Não foi possível validar sua conta no SUAP. Tente novamente.")
        return redirect("portal:index")

    suap_id = str(
        profile.get("matricula")
        or profile.get("identificacao")
        or profile.get("username")
        or profile.get("id")
        or ""
    ).strip()
    if not suap_id:
        messages.error(request, "O SUAP não retornou uma identificação de estudante ou servidor.")
        return redirect("portal:index")

    full_name = str(
        profile.get("nome_usual")
        or profile.get("nome")
        or profile.get("name")
        or suap_id
    ).strip()
    parts = full_name.split(maxsplit=1)
    email = str(profile.get("email") or profile.get("e-mail") or "").strip()
    username = f"suap_{suap_id}"
    User = get_user_model()
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={"first_name": parts[0], "last_name": parts[1] if len(parts) > 1 else ""},
    )
    user.first_name = parts[0]
    user.last_name = parts[1] if len(parts) > 1 else ""
    user.email = email
    user.is_staff = user.is_superuser or suap_id in settings.SUAP_ADMIN_IDS
    user.save(update_fields=["first_name", "last_name", "email", "is_staff"])
    if not user.is_active:
        _revoke_suap_token(access_token)
        messages.error(request, "Esta conta está desativada neste portal. Fale com a equipe responsável.")
        return redirect("portal:index")
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    request.session["suap_access_token"] = access_token

    requested_next = request.session.pop(f"suap_oauth_next:{received_state}", "")
    if requested_next and url_has_allowed_host_and_scheme(
        requested_next,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(requested_next)
    return redirect("portal:management" if user.is_staff else "portal:account")


def _post_suap_form(path, values, authenticate_client=False):
    data = urlencode(values).encode("utf-8")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if authenticate_client:
        # SUAP's confidential OAuth clients authenticate at the token endpoint
        # with HTTP Basic, keeping client credentials out of the form body.
        client_id = quote(settings.SUAP_CLIENT_ID, safe="")
        client_secret = quote(settings.SUAP_CLIENT_SECRET, safe="")
        basic = b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
        headers["Authorization"] = f"Basic {basic}"
    request = Request(
        f"{settings.SUAP_BASE_URL}{path}",
        data=data,
        headers=headers,
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_suap_profile(access_token, scope=""):
    # SUAP replaced the old /api/eu/ user-info endpoint with /api/rh/eu/.
    profile_url = f"{settings.SUAP_BASE_URL}/api/rh/eu/"
    request = Request(
        profile_url,
        headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
    )
    with urlopen(request, timeout=15) as response:
        profile = json.loads(response.read().decode("utf-8"))
    if isinstance(profile, dict) and isinstance(profile.get("data"), dict):
        profile = profile["data"]
    if not isinstance(profile, dict):
        raise ValueError("Formato de perfil SUAP inválido.")
    return profile


def _revoke_suap_token(access_token):
    """Revoke the current SUAP grant so the provider asks consent next time."""
    if not access_token:
        return False
    body = urlencode({
        "token": access_token,
        "token_type_hint": "access_token",
    }).encode("utf-8")
    client_id = quote(settings.SUAP_CLIENT_ID, safe="")
    client_secret = quote(settings.SUAP_CLIENT_SECRET, safe="")
    basic = b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
    request = Request(
        f"{settings.SUAP_BASE_URL}/o/revoke_token/",
        data=body,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            return response.status == 200
    except (HTTPError, URLError, TimeoutError) as exc:
        status = exc.code if isinstance(exc, HTTPError) else type(exc).__name__
        logger.warning("SUAP token revocation failed (%s)", status)
        return False


@login_required
def account(request):
    return render(request, "portal/account.html", {
        "form": CampusItemForm(initial={"kind": CampusItem.Kind.LOST}),
        "demo_login_enabled": False,
        "items": CampusItem.objects.filter(reporter=request.user.pk),
    })


@user_passes_test(lambda user: user.is_staff)
def management(request):
    items = CampusItem.objects.all()
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

    # reporter is stored as a user ID (BigIntegerField) for TiDB compatibility,
    # so resolve names explicitly instead of using select_related.
    items = list(items)
    reporter_ids = {item.reporter for item in items if item.reporter}
    reporters = get_user_model().objects.in_bulk(reporter_ids)
    for item in items:
        reporter = reporters.get(item.reporter)
        item.reporter_display = (
            reporter.get_full_name() or reporter.username
            if reporter else ("Conta removida" if item.reporter else "Comunidade")
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
    access_token = request.session.get("suap_access_token", "")
    revoked = _revoke_suap_token(access_token) if access_token else False
    logout(request)
    if revoked:
        messages.success(request, "Você saiu. Na próxima entrada, o SUAP pedirá autorização novamente.")
    else:
        messages.warning(request, "Você saiu do portal. Não foi possível renovar a autorização do SUAP automaticamente.")
    return redirect("portal:index")
