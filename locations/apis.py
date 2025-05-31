from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError

from locations.services import location_create, location_update, location_delete
from locations.selectors import location_list, location_get, location_get_suitable_for_participants
from locations.models import Location
from users.models import User

class LocationCreateApi(APIView):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=100)
        address = serializers.CharField()
        max_capacity = serializers.IntegerField(min_value=1)  # min_value로 수정
        description = serializers.CharField(required=False, default="")

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        address = serializers.CharField()
        max_capacity = serializers.IntegerField()
        description = serializers.CharField()
        display_capacity = serializers.CharField()
        created_at = serializers.DateTimeField()

    def post(self, request):
        if request.user.user_type != User.UserType.ADMIN:
            return Response(
                {'error': '어드민 권한이 필요합니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            location = location_create(**serializer.validated_data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = self.OutputSerializer(location)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class LocationListApi(APIView):
    """장소 목록 API"""
    permission_classes = [IsAuthenticated]

    class FilterSerializer(serializers.Serializer):
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
        created_at = serializers.DateTimeField()

    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        location = location_list(filters=filter_serializer.validated_data)

        data = self.OutputSerializer(location, many=True).data  # many=True는 여러 객체 직렬화할 때 사용
        return Response(data)


class LocationDetailApi(APIView):
    permission_classes = [IsAuthenticated]

    # URL parameter는 path에서 받으므로 FilterSerializer 불필요
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        address = serializers.CharField()
        max_capacity = serializers.IntegerField()
        description = serializers.CharField()
        display_capacity = serializers.CharField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    def get(self, request, location_id):  # URL parameter로 받음
        try:
            location = location_get(location_id=location_id)
        except Location.DoesNotExist:
            return Response(
                {'error': '장소를 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = self.OutputSerializer(location).data
        return Response(data)


class LocationUpdateApi(APIView):
    """장소 정보 수정 API"""
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=100, required=False)
        address = serializers.CharField(required=False)
        max_capacity = serializers.IntegerField(min_value=1, required=False)
        description = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        address = serializers.CharField()
        max_capacity = serializers.IntegerField()
        description = serializers.CharField()
        display_capacity = serializers.CharField()
        updated_at = serializers.DateTimeField()

    def patch(self, request, location_id):
        if request.user.user_type != User.UserType.ADMIN:
            return Response(
                {'error': '어드민 권한이 필요합니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            location = location_get(location_id=location_id)
        except Location.DoesNotExist:
            return Response(
                {'error': '장소를 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_location = location_update(location=location, data=serializer.validated_data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = self.OutputSerializer(updated_location)
        return Response(output_serializer.data)


class LocationDeleteApi(APIView):
    """장소 삭제 API"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, location_id):
        if request.user.user_type != User.UserType.ADMIN:
            return Response(
                {'error': '어드민 권한이 필요합니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            location = location_get(location_id=location_id)
        except Location.DoesNotExist:
            return Response(
                {'error': '장소를 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            location_delete(location=location)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class LocationSuitableApi(APIView):
    """수용 인원 기준 적절한 장소 목록 API"""
    permission_classes = [IsAuthenticated]

    class FilterSerializer(serializers.Serializer):
        participant_count = serializers.IntegerField(min_value=1)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        max_capacity = serializers.IntegerField()
        display_capacity = serializers.CharField()

    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        location = location_get_suitable_for_participants(
            participant_count=filter_serializer.validated_data['participant_count']
        )

        data = self.OutputSerializer(location, many=True).data
        return Response(data)