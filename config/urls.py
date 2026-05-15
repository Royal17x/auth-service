from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls', namespace='users')),
    path('api/roles/', include('apps.roles.urls', namespace='roles')),
    path('api/resources/', include('apps.resources.urls', namespace='resources')),
]