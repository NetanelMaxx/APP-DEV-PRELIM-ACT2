from django.urls import path
from .views import home

urlpatterns = [
  
    path('', home, name='home'),  # Make sure there's a route for the homepage

]