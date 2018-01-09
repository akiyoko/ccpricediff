from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.PricesIndexView.as_view(), name='index'),
]
