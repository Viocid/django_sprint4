from django.urls import path

from .views import BlogListView, CategoryListView, PostDetailView, PostCreateView, UserProfileView, UserEditView, CommentCreateView, PostDeleteView,PostUpdateView

from .views import edit_post

app_name = "blog"

urlpatterns = [
    path("", BlogListView.as_view(), name="index"),
    path(
        "category/<slug:category_slug>/", CategoryListView.as_view(), name="category_posts"
    ),
    path("posts/<int:id>/", PostDetailView.as_view(), name="post_detail"),
    path('blog/create_post', PostCreateView.as_view(), name='create_post'),
    #path('blog/edit_post/<int:post_id>/', edit_post, name='edit_post'),
    path('blog/<int:pk>/edit', PostUpdateView.as_view(), name='edit_post'),
    path('blog/<int:pk>/delete_post/', PostDeleteView.as_view(), name='delete_post'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='profile'),
    path('profile/<str:username>/edit/', UserEditView.as_view(), name='edit_profile'),
    path('posts/<int:post_id>/comment', CommentCreateView.as_view(), name='add_comment'),
]
