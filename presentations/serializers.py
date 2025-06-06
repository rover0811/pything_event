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
    is_member_comment = serializers.ReadOnlyField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = PresentationComment
        fields = [
            'id', 'presentation', 'content', 'user', 'guest_name',
            'author_name', 'is_member_comment', 'can_edit', 'can_delete',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_can_edit(self, obj):
        request = self.context.get('request')
        return obj.can_edit(request.user if request else None)

    def get_can_delete(self, obj):
        request = self.context.get('request')
        return obj.can_delete(request.user if request else None)

    def create(self, validated_data):
        """댓글 생성"""
        request = self.context.get('request')

        # 인증된 사용자면 회원 댓글로 처리
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
            # guest_name은 clean()에서 자동으로 비워짐
        else:
            # 비인증 사용자는 user를 None으로
            validated_data['user'] = None
            # guest_name이 없으면 clean()에서 자동으로 'Anonymous' 설정

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """댓글 수정 (content만 수정 가능)"""
        request = self.context.get('request')

        if not instance.can_edit(request.user if request else None):
            raise serializers.ValidationError('수정 권한이 없습니다.')

        # content만 수정 가능
        instance.content = validated_data.get('content', instance.content)
        instance.save()  # save()에서 clean() 자동 호출
        return instance