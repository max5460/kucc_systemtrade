from django.urls import path
from . import views
 
urlpatterns = [
    path('Stock/', views.StockView.get, name='get'),
]
