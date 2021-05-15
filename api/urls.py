from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('deleteaccount', views.deleteaccount, name='deleteaccount'),
    path('newpost', views.newpost, name='newpost'),
    path('deletepost', views.deletepost, name='deletepost'),
    path('getcomments', views.getcomments, name='getcomments'),
    path('getposts', views.getposts, name='getposts'),
    path('likepost', views.likepost, name='likepost'),
    path('unlikepost', views.unlikepost, name='unlikepost'),
    path('newcomment', views.newcomment, name='newcomment'),
    path('deletecomment', views.deletecomment, name='deletecomment'),
    path('requestfriend', views.requestfriend, name='requestfriend'),
    path('acceptfriendrequest', views.acceptfriendrequest, name='acceptfriendrequest'),
    path('deletefriendrequest', views.deletefriendrequest, name='deletefriendrequest'),
    path('getfriendrequestsincoming', views.getfriendrequestsincoming, name='getfriendrequestsincoming'),
    path('getfriendrequestsoutgoing', views.getfriendrequestsoutgoing, name='getfriendrequestsoutgoing'),
    path('deletefriendship', views.deletefriendship, name='deletefriendship'),
    path('getprofile', views.getprofile, name="getprofile"),
    path('searchpeople', views.searchpeople, name='searchpeople'),
    path('updateprofilephoto', views.updateprofilephoto, name='updateprofilephoto'),
]
