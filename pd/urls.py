from django.urls import path
#RAJNISH START
from . import views

urlpatterns=[
    path('',views.home,name = 'home'),
    path('register_institutional/',views.register_institutional,name='register_institutional')
]
#RAJNISH END 