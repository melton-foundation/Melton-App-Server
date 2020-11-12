from django.db import models
from markdownx.models import MarkdownxField


class CaseInsensitiveFieldMixin:
    """
    Field mixin that uses case-insensitive lookup alternatives if they exist.
    """

    LOOKUP_CONVERSIONS = {
        "exact": "iexact",
        "contains": "icontains",
        "startswith": "istartswith",
        "endswith": "iendswith",
        "regex": "iregex",
    }

    def get_lookup(self, lookup_name):
        converted = self.LOOKUP_CONVERSIONS.get(lookup_name, lookup_name)
        return super().get_lookup(converted)


class CaseInsensitiveCharField(CaseInsensitiveFieldMixin, models.CharField):
    pass


class Tag(models.Model):
    tag = CaseInsensitiveCharField(max_length=200, unique=True)

    def save(self, *args, **kwargs):
        if not isinstance(self.tag, str):
            self.tag = str(self.tag)
        self.tag = self.tag.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tag


class Post(models.Model):
    title = models.CharField(max_length=200)
    preview = models.ImageField(
        upload_to="post-previews", blank=True, help_text="Preview image for the post"
    )
    description = models.TextField(
        verbose_name="Short Description",
        blank=True,
        help_text="Add a short text describing the post",
    )
    content = MarkdownxField(
        help_text="Write content of post in markdown. To add images, drag and drop them onto the content text field."
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, related_name="posts")

    def update_tags(self, tags):
        if tags is not None and len(tags) > 0:
            existing_tags = list(self.tags.all())
            for tag in existing_tags:
                self.tags.remove(tag)

            for tag in tags:
                if tag.strip() == "":
                    continue
                tag, _ = Tag.objects.get_or_create(tag=tag)
                self.tags.add(tag)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-updated"]
