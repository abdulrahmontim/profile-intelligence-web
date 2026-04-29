PUBLIC_PATHS = ["/login", "/auth/callback", "/auth/github"]

class WebAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path not in PUBLIC_PATHS:
            if not request.session.get("access_token"):
                from django.shortcuts import redirect
                return redirect("/login")
        return self.get_response(request)