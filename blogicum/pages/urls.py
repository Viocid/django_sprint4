from django.urls import path, include
from django.views.generic import TemplateView
from . import views

app_name = "pages"

urlpatterns = [
    path("about/", views.About.as_view(), name="about"),
    path('rules/', views.Rules.as_view(), name='rules'),
]
