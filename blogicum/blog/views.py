from datetime import datetime

from django.shortcuts import get_object_or_404, render

from blog.models import Category, Post

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
