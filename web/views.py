import httpx
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
import httpx
import pycountry


API = settings.API_BASE_URL

# Create your views here.
def require_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get("role") != "admin":
            return redirect("/dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper

def refresh_session(request):
    refresh_token = request.session.get("refresh_token")
    if not refresh_token:
        request.session.flush()
        return False

    response = httpx.post(f"{API}/auth/refresh", json={"refresh_token": refresh_token})
    
    if response.status_code == 200:
        data = response.json()
        request.session["access_token"] = data["access_token"]
        request.session["refresh_token"] = data["refresh_token"]
        request.session.modified = True
        return True
        
    request.session.flush()
    return False

def make_api_call(request, method, path, **kwargs):
    token = request.session.get("access_token")
    
    headers = kwargs.pop("headers", {})
    headers.update({
        "Authorization": f"Bearer {token}",
        "X-API-Version": "1",
    })
    
    url = f"{API}{path}"
    response = httpx.request(method, url, headers=headers, **kwargs)
    
    if response.status_code == 401:
        if refresh_session(request):
            new_token = request.session.get("access_token")
            headers["Authorization"] = f"Bearer {new_token}"
            response = httpx.request(method, url, headers=headers, **kwargs)
            
    return response

def login(request):
    if request.session.get("access_token"):
        return redirect("/dashboard")
        
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
    response = make_api_call(request, "GET", "/api/profiles", params={"limit": 1})
    
    if response.status_code == 401:
        return redirect("/login")

    total = response.json().get("total", 0)
    return render(request, "web/dashboard.html", {
        "total_profiles": total,
        "username": request.session.get("username"),
    })

def resolve_country_id(value):
    if not value:
        return None
    value = value.strip()
    if len(value) == 2:
        return value.upper()
    try:
        results = pycountry.countries.search_fuzzy(value)
        return results[0].alpha_2 if results else value
    except LookupError:
        return value

def profile_list(request):
    params = {k: v for k, v in request.GET.items() if v}

    if "country_id" in params:
        params["country_id"] = resolve_country_id(params["country_id"])

    params.setdefault("page", 1)
    params.setdefault("limit", 10)

    response = make_api_call(request, "GET", "/api/profiles", params=params)
    
    if response.status_code == 401:
        return redirect("/login")

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
    response = make_api_call(request, "GET", f"/api/profiles/{profile_id}")
    if response.status_code == 401:
        return redirect("/login")
        
    profile = response.json().get("data", {})
    return render(request, "web/profile_detail.html", {"profile": profile})

def search(request):
    query = request.GET.get("q", "")
    results = []
    if query:
        response = make_api_call(request, "GET", "/api/profiles/search", params={"q": query})
        if response.status_code == 401:
            return redirect("/login")
            
        results = response.json().get("data", [])
        
    return render(request, "web/search.html", {"results": results, "query": query})

def account(request):
    if not request.session.get("access_token"):
        return redirect("/login")
        
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
            response = make_api_call(
                request, 
                "POST", 
                "/api/profiles/import",
                files={"file": (file.name, file.read(), "text/csv")},
                timeout=300
            )
            
            if response.status_code == 401:
                return redirect("/login")
            elif response.status_code == 200:
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
            response = make_api_call(
                request,
                "POST",
                "/api/profiles",
                json={"name": name},
                timeout=30
            )
            
            if response.status_code == 401:
                return redirect("/login")

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



@require_admin
@require_POST
def profile_delete(request, profile_id):
    
    response = make_api_call(request, "DELETE", f"/api/profiles/{profile_id}")
    
    if response.status_code == 401:
        return redirect("/login")
    
    return redirect("/profiles")

