from django.db.models import Count
from django.utils import timezone

from blog.models import Post


def querying_posts(**kwargs):
    """Запрос постов к базе данных."""
    return (Post.objects.filter(
        is_published=True,
        pub_date__lt=timezone.now(),
        category__is_published=True,
        **kwargs
    )
        .select_related("author", "category", "location")
        .annotate(comments_count=Count("comments"))
        .order_by("-pub_date")
    )
