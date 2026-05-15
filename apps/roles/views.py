from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Role, UserRole, BusinessElement, AccessRolesRule
from .serializers import (
    RoleSerializer,
    BusinessElementSerializer,
    AccessRolesRuleSerializer,
    AssignRoleSerializer,
    RevokeRoleSerializer,
    UserRoleSerializer,
)
from .permissions import IsAdmin


class RoleListCreateView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin]


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin]



class BusinessElementListCreateView(generics.ListCreateAPIView):
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer
    permission_classes = [IsAdmin]


class BusinessElementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer
    permission_classes = [IsAdmin]



class AccessRuleListCreateView(generics.ListCreateAPIView):
    queryset = AccessRolesRule.objects.select_related('role', 'element').all()
    serializer_class = AccessRolesRuleSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        role_id = self.request.query_params.get('role_id')
        if role_id:
            qs = qs.filter(role_id=role_id)
        element = self.request.query_params.get('element')
        if element:
            qs = qs.filter(element__name=element)
        return qs


class AccessRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccessRolesRule.objects.select_related('role', 'element').all()
    serializer_class = AccessRolesRuleSerializer
    permission_classes = [IsAdmin]


class AssignRoleView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_role, created = UserRole.objects.get_or_create(
            user_id=serializer.validated_data['user_id'],
            role_id=serializer.validated_data['role_id'],
        )

        if not created:
            return Response(
                {'message': 'Роль уже назначена этому пользователю.'},
                status=status.HTTP_200_OK,
            )

        return Response(
            {'message': 'Роль успешно назначена.'},
            status=status.HTTP_201_CREATED,
        )


class RevokeRoleView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = RevokeRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        deleted, _ = UserRole.objects.filter(
            user_id=serializer.validated_data['user_id'],
            role_id=serializer.validated_data['role_id'],
        ).delete()

        if not deleted:
            return Response(
                {'error': 'Такой роли у пользователя нет.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({'message': 'Роль снята.'})


class UserRolesView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, user_id):
        roles = UserRole.objects.filter(
            user_id=user_id
        ).select_related('role', 'user')
        serializer = UserRoleSerializer(roles, many=True)
        return Response(serializer.data)


class MyRolesView(APIView):
    def get(self, request):
        roles = UserRole.objects.filter(
            user=request.user
        ).select_related('role')
        return Response([r.role.name for r in roles])