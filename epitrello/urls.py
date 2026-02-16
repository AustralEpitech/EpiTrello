"""
URL configuration for epitrello project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from boards import views as board_views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path("admin/", admin.site.urls),
    # Surcharge de la vue de changement de mot de passe pour inclure l'email
    path(
        "accounts/password_change/",
        board_views.CustomPasswordChangeView.as_view(),
        name="password_change",
    ),
    path("accounts/", include("allauth.urls")),
    path("logout/", board_views.logout_view, name="logout"),
    path("", board_views.home, name="home"),
    path("boards/", include("boards.urls")),
]

