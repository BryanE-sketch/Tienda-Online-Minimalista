
from django.contrib import admin
from django.urls import path

admin.site.site_header = 'Tienda Online Minimalista'
admin.site.site_title = 'Tienda Online'
admin.site.index_title = 'Panel de administración'

urlpatterns = [
    path('admin/', admin.site.urls),
]