from rest_framework import serializers

from posts.models import Post, Tag


class TagSerializer(serializers.RelatedField):
    queryset = Tag.objects.all()

    def to_internal_value(self, data):
        if not isinstance(data, str):
            raise serializers.ValidationError(
                'Only string values are allowed.')

        return data

    def to_representation(self, value):
        return value.tag

    class Meta:
        model = Tag


class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(required=False, many=True)

    class Meta:
        model = Post
        exclude = ('id', 'active')


class PostListSerializer(PostSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'description', 'tags', 'created', 'updated')
