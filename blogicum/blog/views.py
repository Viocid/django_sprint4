from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blog.constants import NUM_PUB_PAGE
from blog.forms import CommentForm, PostForm
from blog.mixins import AuthorRequiredMixin, CommentAuthorMixin
from blog.models import Category, Comment, Post, User
from blog.secondary_func import querying_posts


class BlogListView(ListView):
    model = Post
    template_name = "blog/index.html"
    paginate_by = NUM_PUB_PAGE

    def get_queryset(self):
        return querying_posts()


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    pk_url_kwarg = "post_id"

    def get_object(self, **kwargs):
        post_id = self.kwargs.get("post_id")
        post = super().get_object()
        if post.author == self.request.user:
            return post
        post = get_object_or_404(querying_posts(pk=post_id))
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.select_related(
            "author"
        ).all()
        return context


class CategoryListView(ListView):
    template_name = "blog/category.html"
    paginate_by = NUM_PUB_PAGE

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        category = get_object_or_404(
            Category.objects, slug=category_slug, is_published=True
        )
        self.category = category
        return querying_posts(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class UserProfileView(ListView):
    model = Post
    template_name = "blog/profile.html"
    context_object_name = "profile"
    paginate_by = NUM_PUB_PAGE
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_queryset(self):
        user = get_object_or_404(
            User, username=self.kwargs.get(self.slug_url_kwarg)
        )
        if self.request.user == user:
            return (
                Post.objects.filter(author=user)
                .select_related("author", "category", "location")
                .annotate(comments_count=Count("comments"))
                .order_by("-pub_date")
            )

        return querying_posts()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = get_object_or_404(
            User, username=self.kwargs.get(self.slug_url_kwarg)
        )
        return context


class UserEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "blog/user.html"
    fields = ["first_name", "last_name", "username", "email"]

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def get_success_url(self):
        return reverse(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")
    pk_url_kwarg = "post_id"

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_object(self, queryset=None):
        post = super().get_object()
        if not post.author == self.request.user:
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.object)
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        post_id = self.kwargs["post_id"]
        post = get_object_or_404(Post, id=post_id)
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]}
        )


class CommentUpdateView(LoginRequiredMixin, CommentAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def get_object(self, **kwargs):
        return get_object_or_404(
            Comment,
            pk=self.kwargs.get("comment_id"),
            post=Post.objects.get(pk=self.kwargs.get("post_id")),
            author=self.request.user,
        )

    def get_success_url(self):
        return reverse(
            "blog:post_detail", kwargs={"post_id": self.kwargs.get("post_id")}
        )


class CommentDeleteView(CommentAuthorMixin, DeleteView):
    model = Comment
    pk_url_kwarg = "comment_id"
    template_name = "blog/comment.html"

    def get_success_url(self):
        return reverse(
            "blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]}
        )
