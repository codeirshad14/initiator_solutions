"""initiator2023 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings

from web2 import views
from web2.sitemaps import sitemaps


admin.site.site_header = "INITIATOR SOLUTIONS"
admin.site.site_title = "INITIATOR SOLUTIONS Admin Portal"
admin.site.index_title = "Welcome to INITIATOR SOLUTIONS Associate's Admin Portal"



urlpatterns = [
    path('', views.index, name='index'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap_xml'),
    path('llm.txt', views.llm_txt, name='llm_txt'),
    path('llms.txt', views.llms_txt, name='llms_txt'),
    path('favicon.ico', views.favicon, name='favicon'),
    re_path(r'^(?P<key>[0-9a-f]{32})\.txt$', views.indexnow_key_file, name='indexnow_key_file'),

    path('admin/', admin.site.urls),
    path('web2/', include('web2.urls')),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'web2.views.custom_404'
handler500 = 'web2.views.custom_500'
