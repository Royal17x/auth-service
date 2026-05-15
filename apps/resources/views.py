from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.roles.permissions import has_permission


MOCK_PRODUCTS = [
    {'id': 1, 'name': 'Ноутбук Dell XPS', 'price': 120000, 'owner_id': 1},
    {'id': 2, 'name': 'Смартфон iPhone 15', 'price': 80000, 'owner_id': 2},
    {'id': 3, 'name': 'Наушники Sony WH-1000XM5', 'price': 25000, 'owner_id': 1},
]

MOCK_ORDERS = [
    {'id': 1, 'product_id': 1, 'status': 'pending',   'owner_id': 1, 'total': 120000},
    {'id': 2, 'product_id': 2, 'status': 'completed',  'owner_id': 2, 'total': 80000},
    {'id': 3, 'product_id': 3, 'status': 'processing', 'owner_id': 1, 'total': 25000},
]

MOCK_SHOPS = [
    {'id': 1, 'name': 'TechMart',   'city': 'Москва',  'owner_id': 1},
    {'id': 2, 'name': 'GadgetZone', 'city': 'СПб',     'owner_id': 2},
]


def check_permission(user, element, perm_type):
    if not has_permission(user, element, perm_type):
        return Response(
            {'error': f'Нет права {perm_type} на ресурс {element}.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    return None


class ProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        can_read_all = has_permission(request.user, 'products', 'read_all')
        can_read     = has_permission(request.user, 'products', 'read')

        if not can_read_all and not can_read:
            return Response(
                {'error': 'Нет доступа к продуктам.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if can_read_all:
            return Response({'count': len(MOCK_PRODUCTS), 'results': MOCK_PRODUCTS})

        return Response({'count': 1, 'results': MOCK_PRODUCTS[:1]})

    def post(self, request):
        denied = check_permission(request.user, 'products', 'create')
        if denied:
            return denied
        return Response(
            {'message': 'Продукт создан (mock).', 'data': request.data},
            status=status.HTTP_201_CREATED,
        )


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_product(self, product_id):
        return next((p for p in MOCK_PRODUCTS if p['id'] == product_id), None)

    def get(self, request, pk):
        product = self._get_product(pk)
        if not product:
            return Response({'error': 'Не найдено.'}, status=status.HTTP_404_NOT_FOUND)

        can_read_all = has_permission(request.user, 'products', 'read_all')
        can_read     = has_permission(request.user, 'products', 'read')

        if not can_read_all and not can_read:
            return Response({'error': 'Нет доступа.'}, status=status.HTTP_403_FORBIDDEN)

        return Response(product)

    def patch(self, request, pk):
        product = self._get_product(pk)
        if not product:
            return Response({'error': 'Не найдено.'}, status=status.HTTP_404_NOT_FOUND)

        can_update_all = has_permission(request.user, 'products', 'update_all')
        can_update     = has_permission(request.user, 'products', 'update')

        if not can_update_all and not can_update:
            return Response({'error': 'Нет права на обновление.'}, status=status.HTTP_403_FORBIDDEN)

        return Response({'message': 'Продукт обновлён (mock).', 'data': request.data})

    def delete(self, request, pk):
        product = self._get_product(pk)
        if not product:
            return Response({'error': 'Не найдено.'}, status=status.HTTP_404_NOT_FOUND)

        can_delete_all = has_permission(request.user, 'products', 'delete_all')
        can_delete     = has_permission(request.user, 'products', 'delete')

        if not can_delete_all and not can_delete:
            return Response({'error': 'Нет права на удаление.'}, status=status.HTTP_403_FORBIDDEN)

        return Response({'message': f'Продукт {pk} удалён (mock).'})


class OrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        can_read_all = has_permission(request.user, 'orders', 'read_all')
        can_read     = has_permission(request.user, 'orders', 'read')

        if not can_read_all and not can_read:
            return Response({'error': 'Нет доступа к заказам.'}, status=status.HTTP_403_FORBIDDEN)

        if can_read_all:
            return Response({'count': len(MOCK_ORDERS), 'results': MOCK_ORDERS})

        return Response({'count': 1, 'results': MOCK_ORDERS[:1]})

    def post(self, request):
        denied = check_permission(request.user, 'orders', 'create')
        if denied:
            return denied
        return Response(
            {'message': 'Заказ создан (mock).', 'data': request.data},
            status=status.HTTP_201_CREATED,
        )


class ShopsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        can_read_all = has_permission(request.user, 'shops', 'read_all')
        can_read     = has_permission(request.user, 'shops', 'read')

        if not can_read_all and not can_read:
            return Response({'error': 'Нет доступа к магазинам.'}, status=status.HTTP_403_FORBIDDEN)

        if can_read_all:
            return Response({'count': len(MOCK_SHOPS), 'results': MOCK_SHOPS})

        return Response({'count': 1, 'results': MOCK_SHOPS[:1]})


class MyPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.roles.models import UserRole, AccessRolesRule

        role_ids = UserRole.objects.filter(
            user=request.user
        ).values_list('role_id', flat=True)

        rules = AccessRolesRule.objects.filter(
            role_id__in=role_ids
        ).select_related('element')

        result = {}
        for rule in rules:
            el = rule.element.name
            if el not in result:
                result[el] = {
                    'read': False, 'read_all': False, 'create': False,
                    'update': False, 'update_all': False,
                    'delete': False, 'delete_all': False,
                }
            result[el]['read']       = result[el]['read']       or rule.read_permission
            result[el]['read_all']   = result[el]['read_all']   or rule.read_all_permission
            result[el]['create']     = result[el]['create']     or rule.create_permission
            result[el]['update']     = result[el]['update']     or rule.update_permission
            result[el]['update_all'] = result[el]['update_all'] or rule.update_all_permission
            result[el]['delete']     = result[el]['delete']     or rule.delete_permission
            result[el]['delete_all'] = result[el]['delete_all'] or rule.delete_all_permission

        return Response(result)