from django.urls import path
from . import views

app_name = 'service'
urlpatterns = [
    path('', views.digital_mail_index, name='mail_index'),
]