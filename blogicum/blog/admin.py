from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    empty_value_display = "Не задано"
    list_display = ("title", "location", "is_published")
    list_editable = ("is_published",)
    list_filter = ("category", "location")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published")
    list_editable = ("is_published",)
    list_filter = ("is_published",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "is_published")
    list_editable = ("is_published",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("text", "created_at", "author", "post")
