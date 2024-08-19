"""
URL configuration for myvotingsystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls.static import static
from . import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("myvotingapp.urls"))
]

#This tells Django to serve media files at MEDIA_URL using the directory specified in MEDIA_ROOT.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)# I was getting the error whereby my file was saved in static/images but then the url in admin for the images was localhost/image/image.jpg and it was saying not found and then if i do localhost/static/image/image.jpg I would see the image so i add this and it solved it
