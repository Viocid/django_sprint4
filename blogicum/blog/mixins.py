from django.shortcuts import redirect


class CommentAuthorMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            return redirect("blog:post_detail", post_id=self.object.post_id)
        return super().dispatch(request, *args, **kwargs)


class AuthorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            return redirect("blog:post_detail", post_id=kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)
