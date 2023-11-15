from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

admin.site.site_header = "Streamer Admin Panel"
admin.site.site_title = "Streamer Admin Portal"
admin.site.index_title = "Welcome to Streamer!"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),

    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")),),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
