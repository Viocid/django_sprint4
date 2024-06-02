from datetime import datetime
from django.utils import timezone
from django.urls import reverse_lazy, reverse

from django.db.models.base import Model as Model

from django.db.models.query import QuerySet

from django.shortcuts import get_object_or_404, render, redirect

from django.contrib.auth.decorators import login_required

from blog.models import Category, Post, Comment

from django.views.generic import DetailView, DeleteView, CreateView, UpdateView, ListView

from .forms import PostForm, CommentForm

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import User

from django.core.exceptions import PermissionDenied

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.http import Http404

NUMBER_OF_PUBLICATIONS = 5


def querying_posts(**args):
    """Запрос постов к базе данных."""
    return Post.objects.filter(
        is_published=True,
        pub_date__lt=datetime.now(),
        category__is_published=True,
        **args
    )


class BlogListView(ListView):
    model = Post
    template_name = "blog/index.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_list = querying_posts()
        paginator = Paginator(post_list, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context['page_obj'] = posts
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    context_object_name = "post"

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_object(self, **kwargs):
        post_id = self.kwargs.get('id')
        post = get_object_or_404(Post, pk=post_id)
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(post = self.kwargs.get('id'))
        return context


class CategoryListView(ListView):
    model = Category
    template_name = "blog/category.html"
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(
            Category.objects,
            slug=category_slug,
            is_published=True
        )
        self.category = category
        return querying_posts(category__slug=category_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class UserProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    paginate_by = 10
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts_list = Post.objects.filter(author=self.object).order_by('-pub_date')

        paginator = Paginator(posts_list, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context['page_obj'] = posts
        return context


class UserEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'username', 'email']

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        return self.request.user == self.get_object()


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.instance.pub_date > timezone.now():
            form.instance.is_published = False
        else:
            form.instance.is_published = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('blog:post_detail', id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_object(self, queryset=None):
        post = super(PostDeleteView, self).get_object()
        if not post.author == self.request.user:
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        context['comments'] = Comment.objects.filter(post=self.kwargs.get('id'))
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id)
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'id': self.kwargs['post_id']})


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        comment = self.get_object()
        if comment.author != request.user:
            return redirect('blog:post_detail', pk=comment.post_id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'id': self.kwargs['pk']})
