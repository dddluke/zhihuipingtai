"""test1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include, re_path
from django.conf.urls import url
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework_swagger.views import get_swagger_view
from drf_yasg.views import get_schema_view
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import *
from django.contrib import staticfiles
from One import consumers
from drf_yasg import openapi
# from verifications import urls
schema_view = get_swagger_view(title='API文档')

schema_view = get_schema_view(
    openapi.Info(
        title="API接口文档平台",  # 必传
        default_version='v1',  # 必传
        description="这是一个美轮美奂的接口文档",
        terms_of_service="http://api.xiaogongjin.site",
        contact=openapi.Contact(email="xiaogongjin@qq.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,), # 权限类
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('backendlogin/', admin.site.urls),
    path('one/', include('One.urls')),
    path('text/', include('text.urls')),
    # ('upload',path.join(STATIC_ROOT,'upload').replace('\\','/') ),
    # path('static/', include('static')),
    path(r'chat/', consumers.ChatConsumer),
    path(r'verification/', include('verifications.urls')),
    # path(r'verification/', include('verifications.urls')),
    path(r'docs/', schema_view),
    # path(r'login/', login),
    path(r'', TemplateView.as_view(template_name='index.html')),
    # path(r'blogin/', blogin),

    #第三方登录
    # path('', include('social_django.urls', namespace='social')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(r'swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path(r'redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schemaredoc'),



]
urlpatterns += staticfiles_urlpatterns()