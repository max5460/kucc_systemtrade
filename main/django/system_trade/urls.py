
from django.contrib import admin
from django.conf.urls import url

import manager.views as manager_view

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^Stock/', manager_view.StockView.as_view())
]
