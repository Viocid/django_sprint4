from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from blog.constants import MAX_LENGTH_STR, TEXT_CHAR_LIMIT

User = get_user_model()


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Добавлено"
    )

    class Meta:
        abstract = True


class Location(PublishedModel):
    name = models.CharField(
        max_length=MAX_LENGTH_STR, verbose_name="Название места"
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name[:TEXT_CHAR_LIMIT]


class Category(PublishedModel):
    title = models.CharField(
        max_length=MAX_LENGTH_STR, verbose_name="Заголовок"
    )
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text=(
            "Идентификатор страницы для URL; "
            "разрешены символы латиницы, цифры, дефис и подчёркивание.",
        ),
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title[:TEXT_CHAR_LIMIT]


class Post(PublishedModel):
    title = models.CharField(
        max_length=MAX_LENGTH_STR, verbose_name="Заголовок"
    )
    text = models.TextField(verbose_name="Текст")
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text=(
            "Если установить дату и время в будущем — "
            "можно делать отложенные публикации.",
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Местоположение",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ["-pub_date"]
        default_related_name = "posts"

    def __str__(self):
        return self.title[:TEXT_CHAR_LIMIT]

    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[self.pk])


class Comment(models.Model):
    text = models.TextField(verbose_name="Текст")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Добавлено"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор коментария"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Коментарий"
        verbose_name_plural = "Коментарии"
        default_related_name = "comments"

    def __str__(self):
        return (f'Комментарий автора {self.author.username}'
                f'к посту "{self.post.title}", '
                f'текст: {self.text[:TEXT_CHAR_LIMIT]}')
