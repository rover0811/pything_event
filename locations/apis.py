from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError

from locations.services import location_create, location_update, location_delete
from locations.selectors import location_list, location_get, location_get_suitable_for_participants
from users.models import User


class LocationCreateApi(APIView):
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능하도록 하는 DRF의 권한 클래스

    # 인풋 직렬화
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=100)
        address = serializers.CharField()
        max_capacity = serializers.IntegerField(max_value=1)
        description = serializers.CharField(required=False, default="")

    # 아웃풋 직렬화
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        address = serializers.CharField()
        max_capacity = serializers.IntegerField()
        description = serializers.CharField()

        display_capacity = serializers.CharField()  # 여기 밑으로 필요한가?
        short_address = serializers.CharField()
        created_at = serializers.DateTimeField()

    def post(self, request):
        if request.user.user_type != User.UserType.ADMIN:
            return Response({'error': '어드민 권한이 필요합니다.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializers = self.InputSerializer(data=request)
        serializers.is_valid(raise_exception=True)

        try:
            location = location_create(**serializers.validated_data)
        except ValidationError as e: # 이렇게 에러를 넣어야하나
            return Response({'error': str(e)},status=status.HTTP_400_BAD_REQUEST)

        output_serializer = self.OutputSerializer(location)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED) # 여기서는 검증할 필요가 없으니까 .data를 쓰는 건가


class LocationListApi(APIView):
    """장소 목록 API"""
    permission_classes = [IsAuthenticated]

    class FilterSerializer(serializers.Serializer): # 앞에는 InputSerializer인데 왜 여긴 Filter인가?
        search = serializers.CharField(required=False)
        min_capacity = serializers.IntegerField(required=False, min_value=1)
        max_capacity = serializers.IntegerField(required=False, min_value=1)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        address = serializers.CharField()
        max_capacity = serializers.IntegerField()
        description = serializers.CharField()
        display_capacity = serializers.CharField()
        short_address = serializers.CharField()
        created_at = serializers.DateTimeField()

    def get(self,request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True) # 기본값이 False인가?

        locations = location_list(filters=filter_serializer.validated_data)

        data = self.OutputSerializer(locations,many=True).data # many? 보니까 그냥 시리얼라이저에는 없는 것 같은데
        return Response(data)

class LocationDetailApi(APIView):
    permission_classes = [IsAuthenticated]

    class FilterSerializer(serializers.Serializer):
        id = serializers.UUIDField


    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        address = serializers.CharField()
        max_capacity = serializers.IntegerField()
        description = serializers.CharField()

        display_capacity = serializers.CharField() # 흠
        short_address = serializers.CharField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    def get(self, request):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        location = location_get(location_id=filters_serializer.validated_data)

        data = self.OutputSerializer(location).data
        return Response(data)

