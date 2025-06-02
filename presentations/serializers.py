from rest_framework import serializers
from presentations.models import PresentationComment,Presentation


class PresentationSerializer(serializers.ModelSerializer):
    presenter_name = serializers.CharField(source='presenter.name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    file_name = serializers.CharField(read_only=True)
    file_size_mb = serializers.FloatField(read_only=True)

    class Meta:
        model = Presentation
        fields = '__all__'
        read_only_fields = ['presenter', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['presenter'] = self.context['request'].user
        return super().create(validated_data)


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
