from django import forms
from django.forms import Textarea

from .models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ["title", "text", "pub_date", "location", "category", "image"]
        widgets = {
            "pub_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": Textarea(attrs={"cols": 80, "rows": 20}),
        }
