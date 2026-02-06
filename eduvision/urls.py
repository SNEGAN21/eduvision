from django.contrib import admin
from django.urls import path, include
from accounts import views as account_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", account_views.home, name="home"),   # landing page
   
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("classrooms/", include(("classrooms.urls", "classrooms"), namespace="classrooms")),
    path("engagement/", include(("engagement.urls", "engagement"), namespace="engagement")),
   
    
]
