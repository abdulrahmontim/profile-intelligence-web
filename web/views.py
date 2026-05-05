import httpx
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
import httpx


API = settings.API_BASE_URL

# Create your views here.

def require_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get("role") != "admin":
            return redirect("/dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


def api_get(request, path, params=None):
    token = request.session.get("access_token")
    return httpx.get(
        f"{API}{path}",
        params=params,
        headers={
            "Authorization": f"Bearer {token}",
            "X-API-Version": "1",
        },
        timeout=10,
    )


def refresh_session(request) -> bool:
    refresh_token = request.session.get("refresh_token")
    if not refresh_token:
        return False

    response = httpx.post(f"{API}/auth/refresh",
                         json={"refresh_token": refresh_token})
    if response.status_code == 200:
        data = response.json()
        request.session["access_token"] = data["access_token"]
        request.session["refresh_token"] = data["refresh_token"]
        return True
    return False


def login(request):
    return render(request, "web/login.html")


def github_redirect(request):
    return redirect(f"{API}/auth/github")


def auth_callback(request):
    access_token = request.GET.get("access_token")
    refresh_token = request.GET.get("refresh_token")
    username = request.GET.get("username")
    role = request.GET.get("role")

    if not access_token:
        return redirect("/login?error=auth_failed")

    request.session["access_token"] = access_token
    request.session["refresh_token"] = refresh_token
    request.session["username"] = username
    request.session["role"] = role

    return redirect("/dashboard")


def logout(request):
    refresh_token = request.session.get("refresh_token")
    if refresh_token:
        httpx.post(f"{API}/auth/logout", json={"refresh_token": refresh_token})
    request.session.flush()
    return redirect("/login")


def dashboard(request):
    response = api_get(request, "/api/profiles", {"limit": 1})
    if response.status_code == 401:
        if not refresh_session(request):
            return redirect("/login")
        response = api_get(request, "/api/profiles", {"limit": 1})

    total = response.json().get("total", 0)
    return render(request, "web/dashboard.html", {
        "total_profiles": total,
        "username": request.session.get("username"),
    })


def profile_list(request):
    params = {k: v for k, v in request.GET.items() if v}
    params.setdefault("page", 1)
    params.setdefault("limit", 10)

    response = api_get(request, "/api/profiles", params)
    if response.status_code == 401:
        if not refresh_session(request):
            return redirect("/login")
        response = api_get(request, "/api/profiles", params)

    data = response.json()
    current_page = int(params["page"])
    total_pages = data.get("total_pages", 1)

    def build_url(page):
        updated = {**params, "page": page}
        return "/profiles?" + "&".join(f"{k}={v}" for k, v in updated.items())

    return render(request, "web/profiles.html", {
        "data": data,
        "prev_url": build_url(current_page - 1) if current_page > 1 else None,
        "next_url": build_url(current_page + 1) if current_page < total_pages else None,
    })


def profile_detail(request, profile_id):
    response = api_get(request, f"/api/profiles/{profile_id}")
    profile = response.json().get("data", {})
    return render(request, "web/profile_detail.html", {"profile": profile})


def search(request):
    query = request.GET.get("q", "")
    results = []
    if query:
        response = api_get(request, "/api/profiles/search", {"q": query})
        results = response.json().get("data", [])
    return render(request, "web/search.html", {"results": results, "query": query})


def account(request):
    return render(request, "web/account.html", {
        "username": request.session.get("username"),
        "role": request.session.get("role"),
    })
    
    
@require_admin
def profile_import(request):
    result = None
    message = None
    message_type = None

    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            message = "No file selected"
            message_type = "error"
        else:
            token = request.session.get("access_token")
            response = httpx.post(
                f"{API}/api/profiles/import/",
                files={"file": (file.name, file.read(), "text/csv")},
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-API-Version": "1",
                },
                timeout=300,
            )
            if response.status_code == 200:
                result = response.json()
            else:
                message = "Upload failed. Please try again."
                message_type = "error"

    return render(request, "web/import.html", {
        "result": result,
        "message": message,
        "message_type": message_type,
    })


@require_admin
def profile_create(request):
    profile = None
    message = None
    message_type = None

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            message = "Name is required"
            message_type = "error"
        else:
            token = request.session.get("access_token")
            response = httpx.post(
                f"{API}/api/profiles/",
                json={"name": name},
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-API-Version": "1",
                },
                timeout=30,
            )
            data = response.json()
            if response.status_code in (200, 201):
                profile = data.get("data")
                message = "Profile created successfully"
                message_type = "success"
            else:
                message = data.get("message", "Failed to create profile")
                message_type = "error"

    return render(request, "web/create_profile.html", {
        "profile": profile,
        "message": message,
        "message_type": message_type,
    })