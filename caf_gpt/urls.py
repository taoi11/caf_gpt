"""
CAF_GPT URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import csp_report_view

urlpatterns = [
    path('', include('core.urls')),
    path('pacenote/', include('pacenote_foo.urls')),
    path('policy/', include('policy_foo.urls')),
    path('csp-report/', csp_report_view, name='csp_report_view'),
]

# Add admin URLs only in development
if settings.DEBUG:
    urlpatterns.insert(0, path('admin/', admin.site.urls))

# Add debug toolbar URLs in development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    # Serve static and media files in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
