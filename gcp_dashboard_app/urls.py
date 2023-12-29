from django.urls import path,include
from . import views
urlpatterns = [
    path("",views.home),
    path("get-instances/", views.get_instance_details, name="get_instance_details"),
    path("logout",views.logout_view),
]