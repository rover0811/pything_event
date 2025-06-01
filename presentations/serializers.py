from rest_framework import serializers
from presentations.models import PresentationComment


class PresentationCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField()

    class Meta:
        model = PresentationComment
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        if self.context['request'].user.is_authenticated:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
