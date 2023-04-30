from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.home,name='home'),
    path('screened/', views.screened,name='screened'),
    path('jobdesc/',views.getJobDescription,name='jobdesc'),
    path('details/<id>',views.details,name='details'),
]
