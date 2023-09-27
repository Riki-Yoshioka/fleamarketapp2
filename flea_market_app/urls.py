"""
URL configuration for flea_market_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
# settings 追加
from django.conf import settings
# include 追加
from django.urls import path, include
from django.contrib.staticfiles.urls import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("main.urls")), # 追加
    path("accounts/", include("accounts.urls")), # allauth にない機能でアカウントに関連するものを accounts アプリ内で実行するためのルーティング
    path("accounts/", include("allauth.urls")), # allauth を使うためのルーティング
]
# 追加

if settings.DEBUG:
    # 追加
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]