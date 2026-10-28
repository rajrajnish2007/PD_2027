
from django.urls import path
from . import views

app_name = 'registration'

urlpatterns = [
    path(
        'register/independent-adjudicator/',
        views.register_adjudicator,
        name='register_adjudicator'
    ),
]
