from django.conf import settings
from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from pages.views import page_not_found, server_error, csrf_failure
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect

handler403 = 'pages.views.csrf_failure'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns = [
    path("admin/", admin.site.urls,),
    path("pages/", include("pages.urls", namespace="pages",),),
    path("", include("blog.urls", namespace="blog",),),
    path('auth/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    path('auth/password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('auth/password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('auth/password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('auth/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('auth/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('auth/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('auth/registration/', CreateView.as_view(template_name='registration/registration_form.html', form_class=UserCreationForm, success_url=reverse_lazy('blog:index')), name='registration'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
