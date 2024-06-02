from django.urls import path

from .views import BlogListView, CategoryListView, PostDetailView, PostCreateView, UserProfileView, UserEditView, CommentCreateView, CommentDeleteView, PostDeleteView, PostUpdateView, CommentUpdateView

app_name = "blog"

urlpatterns = [
    path("", BlogListView.as_view(), name="index"),
    path(
        "category/<slug:category_slug>/", CategoryListView.as_view(), name="category_posts"
    ),
    path("posts/<int:id>/", PostDetailView.as_view(), name="post_detail"),
    path('posts/create/', PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/edit/', PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/delete/', PostDeleteView.as_view(), name='delete_post'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='profile'),
    path('profile/<str:username>/edit/', UserEditView.as_view(), name='edit_profile'),
    path('posts/<int:post_id>/comment', CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:pk>/delete_comment/<int:comment_id>/',CommentDeleteView.as_view(), name='delete_comment'),
]
