from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from .views import AuthRegistration

handler403 = "pages.views.csrf_failure"
handler404 = "pages.views.page_not_found"
handler500 = "pages.views.server_error"

urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "pages/",
        include(
            "pages.urls",
            namespace="pages",
        ),
    ),
    path(
        "",
        include(
            "blog.urls",
            namespace="blog",
        ),
    ),
    path(
        "auth/registration/",
        AuthRegistration.as_view(),
        name="registration",
    ),
    path("auth/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
