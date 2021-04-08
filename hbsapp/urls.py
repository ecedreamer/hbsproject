from django.urls import path
from .views import *

app_name = "hbsapp"
urlpatterns = [
    # client urls
    path("", ClientHomeView.as_view(), name="clienthome"),
    path("room-<room_code>-<int:pk>/",
         ClientRoomDetailView.as_view(), name="clientroomdetail"),
    # customer urls
    path("register/", CustomerRegisterView.as_view(), name="customerregister"),
    path("login/", CustomerLoginView.as_view(), name="customerlogin"),
    path("logout/", CustomerLogoutView.as_view(), name="customerlogout"),

    path("room-<int:pk>-check/",
         CustomerRoomCheckView.as_view(), name="customerroomcheck"),
    path("room-<int:pk>-book/",
         CustomerRoomBookingView.as_view(), name="customerroombooking"),

    path("customer-profile/",
         CustomerProfileView.as_view(), name="customerprofile"),

    # admin urls
    path("admin-login/", AdminLoginView.as_view(), name="adminlogin"),
    path("admin-logout/", AdminLogoutView.as_view(), name="adminlogout"),

    path("system-admin/", AdminHomeView.as_view(), name="adminhome"),
    path("system-admin/hotel-list/",
         AdminHotelListView.as_view(), name="adminhotellist"),
    path("system-admin/hotel-create/",
         AdminHotelCreateView.as_view(), name="adminhotelcreate"),
    path("system-admin/hotel-<int:pk>-update/",
         AdminHotelUpdateView.as_view(), name="adminhotelupdate"),

    path("system-admin/room-list/",
         AdminRoomListView.as_view(), name="adminroomlist"),
    path("system-admin/room-create/",
         AdminRoomCreateView.as_view(), name="adminroomcreate"),
]
