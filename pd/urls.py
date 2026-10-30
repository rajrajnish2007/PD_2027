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
]