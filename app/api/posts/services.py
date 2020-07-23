from posts.models import Post


def get_post_tags(id=None, post=None):
    tags = []
    if id is not None:
        post = Post.objects.filter(pk=id).first()

    if post is not None:
        tags = [tag.tag for tag in post.tags.all()]

    return tags
