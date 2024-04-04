from django.urls import path
from . import views

urlpatterns = [
    # path('', views.login, name='login'),
    path('index', views.index, name='index'),
    path('listproject', views.listproject, name='listproject'),
    path('updateproject/<str:id>', views.updateproject, name='updateproject'),
    path('listissue/<str:id>', views.listissue, name='listissue'),
    path('listdetails/<str:id>', views.listdetails, name='listdetails'),
    path('updateissue/<str:id>', views.updateissue, name='updateissue'),
    path('deleteissue/<str:id>', views.deleteissue, name='deleteissue'),
    path('export/<str:id>', views.export, name='export'),
    path('newissue', views.newissue, name='newissue'),
    path('newproject', views.newproject, name='newproject'),
    path('confirmation/<str:name>', views.confirmation, name='confirmation'),
    path('addrelation/<str:id>', views.addrelations, name='addrelation'),
    path('register', views.register, name='register'),
    path('', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('settings', views.settings, name='settings'),
    path('email', views.email, name='email')
]