from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),

    path('election/<str:pk>', views.viewElection, name="viewElection"),
    path('submitVote', views.submitVote, name="submitVote"),
    path('viewVotes/<str:pk>', views.viewVotes, name="viewVotes"),
    path('create-election/', views.create_election, name='create_election'),
    path('election/<int:pk>/delete/', views.delete_election, name='delete_election'),
    path('election/<int:pk>/add-contestant/', views.add_contestant, name='add_contestant'),

    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('signup', views.signup, name='signup'),
]
