from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from django.forms import ModelForm, TextInput, CharField

from posts.models import Post, Tag
from posts import services


class PostForm(ModelForm):

    tags_display = CharField(
        label='Tags', help_text='Enter comma separated values', required=False, widget=TextInput(attrs={'class': 'vTextField'}))

    def __init__(self, *args, **kwargs):
        self._tags = []
        tag_values = []
        if 'instance' in kwargs and kwargs['instance'] is not None:
            tag_values = services.get_post_tags(id=kwargs['instance'].id)
        super().__init__(*args, **kwargs)
        if self.initial != {}:
            self.initial['tags_display'] = ' , '.join(tag_values)

    def save(self, *args, **kwargs):
        self._tags = [tag.strip() for tag in self.cleaned_data.get(
            'tags_display', '').split(',')]
        post = super().save()
        post.update_tags(self._tags)
        return post

    def save_m2m(self, *args, **kwargs):
        # Do not remove this method. It fails saying method not found. Yet to figure out how to avoid this completely
        pass

    class Meta:
        model = Post
        exclude = ('tags', )


class PostAdmin(MarkdownxModelAdmin):
    model = Post
    form = PostForm
    list_display = ('title', 'created', 'updated', 'active')
    list_editable = ('active', )


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
