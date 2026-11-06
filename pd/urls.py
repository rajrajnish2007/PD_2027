from django.urls import path
from . import views
app_name = 'registration'
urlpatterns=[
    path('',views.home,name = 'home'),
    path('register_institutional/',views.register_institutional,name='register_institutional'),
    path(
        'register/independent-adjudicator/',
        views.register_adjudicator,
        name='register_adjudicator'
    ),
    # RAJNISH START
    path('register/cross/', views.register_cross, name='register_cross'),
    path('register_cross/', views.register_cross, name='register_cross_direct'),
    # RAJNISH END
]
