from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('qr_mobile/<mobile>/<amount>/qr.png', views.get_qr, name='qr'),
    path('qrcode/',views.qrcode, name='qrcode'),
    path('index/',views.index, name='index'),
    # path('qr_mobile/<mobile>/<amount>/qr.png', views.get_qr, name='qr'),
]
