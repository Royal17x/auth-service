from django.urls import path
from . import views

app_name = 'roles'

urlpatterns = [
    path('', views.RoleListCreateView.as_view(), name='role-list'),
    path('<int:pk>/', views.RoleDetailView.as_view(), name='role-detail'),

    path('elements/', views.BusinessElementListCreateView.as_view(), name='element-list'),
    path('elements/<int:pk>/', views.BusinessElementDetailView.as_view(), name='element-detail'),

    path('rules/', views.AccessRuleListCreateView.as_view(), name='rule-list'),
    path('rules/<int:pk>/', views.AccessRuleDetailView.as_view(), name='rule-detail'),

    path('assign/', views.AssignRoleView.as_view(), name='assign'),
    path('revoke/', views.RevokeRoleView.as_view(), name='revoke'),
    path('user/<uuid:user_id>/', views.UserRolesView.as_view(), name='user-roles'),
    path('my/', views.MyRolesView.as_view(), name='my-roles'),
]