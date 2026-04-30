from django.urls import path
from . import views

urlpatterns = [
    path("", views.login, name="login"),
    path("login", views.login, name="login"),
    path("auth/github", views.github_redirect, name="github_redirect"),
    path("auth/callback", views.auth_callback, name="auth_callback"),
    path("logout", views.logout, name="logout"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("profiles", views.profile_list, name="profiles"),
    path("profiles/<str:profile_id>", views.profile_detail, name="profile_detail"),
    path("search", views.search, name="search"),
    path("account", views.account, name="account"),
]