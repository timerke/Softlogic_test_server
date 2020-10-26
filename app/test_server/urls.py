from django.contrib import admin
from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^about/', views.about, name='about'),
    url(r'^api/v1/persons/(?P<obj_id>(.)+)/', views.get_info),
    url(r'^api/v1/persons/', views.post_get_put, name='persons'),
    url(r'^api/v1/compare/', views.compare, name='compare'),
    url(r'', views.index, name='home')
]
