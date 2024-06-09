from django.urls import include, path

from .views import (
    BlogListView,
    CategoryListView,
    CommentCreateView,
    CommentDeleteView,
    CommentUpdateView,
    PostCreateView,
    PostDeleteView,
    PostDetailView,
    PostUpdateView,
    UserEditView,
    UserProfileView,
)

app_name = "blog"

posts_urls = [
    path(
        "<int:post_id>/delete/", PostDeleteView.as_view(), name="delete_post"
    ),
    path("<int:post_id>/edit/", PostUpdateView.as_view(), name="edit_post"),
    path("create/", PostCreateView.as_view(), name="create_post"),
    path("<int:post_id>/", PostDetailView.as_view(), name="post_detail"),
    path(
        "<int:post_id>/comment/",
        CommentCreateView.as_view(),
        name="add_comment",
    ),
    path(
        "<int:post_id>/edit_comment/<int:comment_id>/",
        CommentUpdateView.as_view(),
        name="edit_comment",
    ),
    path(
        "<int:post_id>/delete_comment/<int:comment_id>/",
        CommentDeleteView.as_view(),
        name="delete_comment",
    ),
]

urlpatterns = [
    path("", BlogListView.as_view(), name="index"),
    path(
        "category/<slug:category_slug>/",
        CategoryListView.as_view(),
        name="category_posts",
    ),
    path("posts/", include(posts_urls)),
    path(
        "profile/edit/",
        UserEditView.as_view(),
        name="edit_profile",
    ),
    path("profile/<str:username>/", UserProfileView.as_view(), name="profile"),
]
