from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', RedirectView.as_view(url='/accounts/login/')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^prices/', include('prices.urls', namespace='prices')),
]
