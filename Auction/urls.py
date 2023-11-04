from django.urls import path
from . import views

#URLconfg
urlpatterns=[
    #expected that userid can be fetched using the session
    path("home/",views.DisplayCategory), #tested and approved
    path("home/initiate_auction/",views.initiateAuction), #tested and approved
    path("home/<str:categoryName>/",views.DisplayAuctions), #tested and approved
    path("home/<str:categoryName>/<int:itemId>/",views.DisplayBids), #tested and approved
    path("home/<str:categoryName>/<int:itemId>/place_bid/",views.placeBid), #tested and approved
    path("home/<str:categoryName>/<int:itemId>/erase_bid",views.eraseBid), #tested and approved
    path("home/<int:userId>/",views.get_user), #go to profile page
]
