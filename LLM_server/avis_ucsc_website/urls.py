"""
URL configuration for avis_ucsc_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
    
    path("", views.dashboard, name="dashboard"),

    path("world_map/", views.world_map, name="world_map"),
    path("baskin_world_links/", views.baskin_world_links, name="baskin_world_links"),

    path("llm/", views.llm_page, name="llm_page"),
    path("ask-llm/", views.ask_llm, name="ask_llm"),

    # path("localize/", views.localize, name="localize"),
    # path("api/localize/", views.localize_api, name="localize_api"),

    path("viewer/", views.viewer, name="viewer"),


    path("upload_vrs/", views.upload_vrs_page, name="upload_vrs_page"),
    path("api/upload_vrs/", views.upload_vrs_api, name="upload_vrs_api"),


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])