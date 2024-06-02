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


def index(request):
    post_list = querying_posts()[:NUMBER_OF_PUBLICATIONS]
    context = {"post_list": post_list}
    template = "blog/index.html"
    return render(request, template, context)


def post_detail(request, id):
    post = get_object_or_404(
        querying_posts(pk=id)
    )
    context = {"post": post}
    template = "blog/detail.html"
    return render(request, template, context)


def category_posts(request, category_slug):
    post_list = querying_posts(
        category__slug=category_slug
    )
    category = get_object_or_404(
        Category.objects,
        slug=category_slug,
        is_published=True
    )
    context = {"category": category, "post_list": post_list}
    template = "blog/category.html"
    return render(request, template, context)


class BlogListView(ListView):
    model = Post
    template_name = "blog/index.html"
    paginate_by = 10

    def get_object(self, **kwargs):
        post_list = querying_posts()
        return post_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = self.get_object()
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    #context_object_name = "post"

    def get_object(self, **kwargs):
        id_ = self.kwargs.get('id')
        post = get_object_or_404(querying_posts(pk=id_))
        user = self.request.user.id
        if post.author == self.request.user:
            post = Post.objects.filter(pk=id_)
            return post
        else:
            return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context


class CategoryListView(ListView):
    model = Category
    template_name = "blog/category.html"
    #context_object_name = "page_obj"
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
        #context = super().get_context_data(**kwargs)
        #context['posts'] = Post.objects.filter(author=self.object)
        #return context
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
    fields = ['first_name', 'last_name', 'username', 'email']
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('profile')
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})

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

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:profile')

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
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    pass

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})
