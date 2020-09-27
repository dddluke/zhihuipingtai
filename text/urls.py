from django.urls import path
from django.conf.urls import url
from django.urls import include
from .views import *
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token
from text import views

app_name = "text"

urlpatterns = [
    url(r'^editblog', views.edit_blog, name='edit_blog'),
    # (r'^tinymce/', include('tinymce.urls')),
    path('post', publish, name='post'),
    path('showpost', show_post, name='showpost')
]