
from django.contrib import admin
from django.urls import path, include

# for static settings
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('users.urls')),
]
# to upload image we need to specify to where to look for imag url
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
