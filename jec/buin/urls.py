from django.urls import path
from . import views

urlpatterns = [
    # URL untuk visualisasi star schema
    path('visualize/', views.display_star_schema, name='display_star_schema'),
]