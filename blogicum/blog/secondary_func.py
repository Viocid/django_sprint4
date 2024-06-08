from django.utils import timezone

from blog.models import Post


def querying_posts(**kwargs):
    """Запрос постов к базе данных."""
    return Post.objects.filter(
        is_published=True,
        pub_date__lt=timezone.now(),
        category__is_published=True,
        **kwargs
    )
