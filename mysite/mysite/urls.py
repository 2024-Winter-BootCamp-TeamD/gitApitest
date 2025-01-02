"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from mysite.views import github_oauth, github_oauth_callback, org_list, org_repos, setup_webhook, github_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    # GitHub OAuth 인증
    path('github/oauth/', github_oauth, name='github_oauth'),
    path('github/oauth/callback/',github_oauth_callback, name='github_oauth_callback'),

    # 조직 목록 및 리포지토리 목록 페이지
    path('github/orgs/', org_list, name='org_list'),
    path('github/orgs/<str:org_name>/repos/', org_repos, name='org_repos'),

    # 리포지토리에 웹훅 설정
    path('github/orgs/<str:org_name>/repos/<str:repo_name>/setup-webhook/', setup_webhook, name='setup_webhook'),

    # GitHub에서 웹훅 이벤트를 수신하는 엔드포인트
    path('github/webhook/',github_webhook, name='github_webhook'),
]
