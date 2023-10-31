from django.urls import path
from . import views

#URLconfg
urlpatterns=[
    #expected that userid can be fetched using the session
    path("home/",views.home),
    path("home/<str:category>/",views.DisplayAuctions),
    path("home/<int:itemId>/",views.DisplayCategory),#filter its category and redirect to the below path accordingly
    path("home/<str:category>/<int:itemId>/",views.DisplayBids),
    path("home/<str:category>/<int:itemId>/place_bid",views.placeBid),
    path("home/<str:category>/<int:itemId>/erase_bid",views.eraseBid),
    path("home/<int:userId>/",views.get_user), #go to profile page
    path("home/intiate_auction",views.initiateAuction), #start the auction
]
