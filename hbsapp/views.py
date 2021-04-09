from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import date
from .forms import *


class ClientMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.context = {
            "roomtypes": ROOM_TYPE
        }
        return super(ClientMixin, self).dispatch(request, *args, **kwargs)


class ClientHomeView(ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["popular_rooms"] = HotelRoom.objects.order_by("-view_count")
        return render(request, "clienttemplates/clienthome.html", context)


class ClientRoomDetailView(ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        try:
            room = HotelRoom.objects.get(id=self.kwargs.get("pk"))
            context["room"] = room
            context["roombookingform"] = RoomBookingForm
            room.view_count += 1
            room.save()
            return render(request, "clienttemplates/clientroomdetail.html", context)
        except Exception as e:
            messages.error(request, "Hotel not found.")
            return redirect("hbsapp:clienthome")


# customer views
class CustomerRegisterView(ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["registrationform"] = CustomerRegistrationForm
        return render(request, "clienttemplates/customerregister.html", context)

    def post(self, request, *args, **kwargs):
        context = self.context
        registrationform = CustomerRegistrationForm(request.POST)
        if registrationform.is_valid():
            email = registrationform.cleaned_data.get("email")
            password = registrationform.cleaned_data.get("password")
            mobile = registrationform.cleaned_data.get("mobile")
            if not User.objects.filter(username=email).exists():
                user = User.objects.create_user(email, email, password)
                Customer.objects.create(user=user, mobile=mobile)
                login(request, user)
                messages.success(request, "You are registered successfully.")
                if "next" in request.GET:
                    next_url = request.GET.get("next")
                    return redirect(next_url)
                else:
                    return redirect("hbsapp:clienthome")
            else:
                context["registrationform"] = CustomerRegistrationForm
                context["error"] = "Invalid attempts"
                messages.error(request, "Invalid attempts to register...")
                return render(request, "clienttemplates/customerregister.html", context)
        else:

            context["registrationform"] = CustomerRegistrationForm
            context["error"] = "Invalid attempts"
            messages.error(request, "Invalid attempts to register.")
            return render(request, "clienttemplates/customerregister.html", context)


class CustomerLoginView(ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["loginform"] = LoginForm
        return render(request, "clienttemplates/customerlogin.html", context)

    def post(self, request, *args, **kwargs):
        loginform = LoginForm(request.POST, None)
        if loginform.is_valid():

            email = loginform.cleaned_data.get("email")
            password = loginform.cleaned_data.get("password")
            user = authenticate(username=email, password=password)
            try:
                customer = user.customer
                login(request, user)
                messages.success(request, "Successfully logged in.")
                if "next" in request.GET:
                    next_url = request.GET.get("next")
                    return redirect(next_url)
                else:
                    return redirect(reverse("hbsapp:clienthome"))
            except Exception as e:
                print(e)
                messages.error(request, "Invalid username or password..")
                context = {
                    "loginform": LoginForm,
                    "error": "Invalid username or password."
                }
                return render(request, "clienttemplates/customerlogin.html", context)
        else:
            context = {
                "loginform": LoginForm,
                "error": "Invalid username or password."
            }
            return render(request, "clienttemplates/customerlogin.html", context)


class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "Successfully logged out")
        return redirect("hbsapp:clienthome")


class CustomerRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        try:
            self.customer = request.user.customer
        except Exception as e:
            print(e)
            return redirect(reverse("hbsapp:customerlogin") + "?next=" + request.path)
        return super(CustomerRequiredMixin, self).dispatch(request, *args, **kwargs)


class CustomerRoomCheckView(ClientMixin, View):
    def get(self, request, *args, **kwargs):
        room = HotelRoom.objects.get(id=self.kwargs.get("pk"))
        booking_starts = request.GET.get("date")
        booking_for = date.fromisoformat(booking_starts)
        if booking_for >= timezone.now().date() :
            rb = RoomBooking.objects.filter(hotel_room=room, booking_starts__lte=booking_starts, booking_ends__gte=booking_starts)
            if rb.exists():
                room_status = "unavailable"
            else:
                room_status = "available"
        else:
            room_status = "error"
        resp = {
            "status": room_status
        }
        return JsonResponse(resp)



class CustomerRoomBookingView(CustomerRequiredMixin, ClientMixin, View):
    def post(self, request, *args, **kwargs):
        try:

            room = HotelRoom.objects.get(id=self.kwargs.get("pk"))
            context = self.context
            booking_form = RoomBookingForm(request.POST)
            if booking_form.is_valid():
                booking = booking_form.save(commit=False)
                booking.hotel_room = room
                booking.customer = request.user.customer
                booking.booking_status = "Pending"
                stay_days = booking_form.cleaned_data.get("booking_ends") - booking_form.cleaned_data.get("booking_starts")
                stay_days = 1 if stay_days.days == 0 else stay_days.days
                booking.amount = room.price * booking_form.cleaned_data.get("total_persons") * stay_days
                booking.save()
                return redirect(reverse("hbsapp:customerbookingdetail", kwargs={"pk": booking.id}) + "?b=s")
            else:
                messages.error(request, "Something went wrong..")
                return redirect("hbsapp:clientroomdetail", room_code=room.room_code, pk=room.id)
        except Exception as e:
            messages.error(request, "Room not found..")
            print(e)
            return redirect("hbsapp:clienthome")


class CustomerProfileView(CustomerRequiredMixin, ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        customer = request.user.customer
        context["customer"] = customer
        context["allbookings"] = RoomBooking.objects.filter(customer=customer).order_by("-id")
        return render(request, "clienttemplates/customerprofile.html", context)


class CustomerBookingDetailView(CustomerRequiredMixin, ClientMixin, View):

    def get(self, request, *args, **kwargs):
        context = self.context
        try:
            context["booking"] = RoomBooking.objects.get(id=self.kwargs.get("pk"), customer=request.user.customer)
            return render(request, "clienttemplates/customerbookingdetail.html", context)
        except Exception as e:
            messages.error(request, "You are not allowed to view this page.")
            return redirect("hbsapp:clienthome")


# admin views


class AdminLoginView(View):
    def get(self, request, *args, **kwargs):
        context = {
            "loginform": LoginForm
        }
        return render(request, "admintemplates/adminlogin.html", context)

    def post(self, request, *args, **kwargs):
        loginform = LoginForm(request.POST, None)
        if loginform.is_valid():

            email = loginform.cleaned_data.get("email")
            password = loginform.cleaned_data.get("password")
            user = authenticate(username=email, password=password)
            try:
                admin = user.admin
                login(request, user)
                return redirect(reverse("hbsapp:adminhome"))
            except Exception as e:
                print(e)
                context = {
                    "loginform": LoginForm,
                    "error": "Invalid username or password."
                }
                return render(request, "admintemplates/adminlogin.html", context)
        else:
            context = {
                "loginform": LoginForm,
                "error": "Invalid username or password."
            }
            return render(request, "admintemplates/adminlogin.html", context)


class AdminLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "Successfully logged out")
        return redirect("hbsapp:adminlogin")


class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.admin = request.user.admin
            self.context = {
                "admin": self.admin
            }
        except Exception as e:
            print(e)
            return redirect(reverse("hbsapp:adminlogin") + "?next=" + request.path)
        return super(AdminRequiredMixin, self).dispatch(request, *args, **kwargs)


class AdminHomeView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        return render(request, "admintemplates/adminhome.html", context)


class AdminHotelListView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["hotellist"] = Hotel.objects.all()
        return render(request, "admintemplates/adminhotellist.html", context)


class AdminHotelCreateView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["hotelform"] = HotelForm
        return render(request, "admintemplates/adminhotelcreate.html", context)

    def post(self, request, *args, **kwargs):
        hotelform = HotelForm(request.POST, request.FILES)
        if hotelform.is_valid():
            hotelform.save()
            messages.success(request, "New hotel added successfully.")
        else:
            context = {}
            messages.error(request, "Error creating new hotel.")
            return render(request, "admintemplates/adminhotelcreate.html", context)
        return redirect("hbsapp:adminhotellist")


class AdminHotelUpdateView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        try:
            hotel = Hotel.objects.get(id=self.kwargs.get("pk"))
            context["hotelform"] = HotelForm(instance=hotel)
            return render(request, "admintemplates/adminhotelcreate.html", context)
        except Exception as e:
            print(e)
            messages.error(request, "Hotel not found.")
            return redirect("hbsapp:adminhotellist")

    def post(self, request, *args, **kwargs):
        try:
            hotel = Hotel.objects.get(id=self.kwargs.get("pk"))
            hotel.name = request.POST.get("name")
            hotel.address = request.POST.get("address")
            hotel.image = request.FILES.get("image")
            hotel.email = request.POST.get("email")
            hotel.contact = request.POST.get("contact")
            hotel.save()
            messages.success(request, "Data updated successfully.")
        except Exception as e:
            print(e)
            messages.error(request, "Can not save the data.")
        return redirect("hbsapp:adminhotellist")


class AdminRoomListView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["roomlist"] = HotelRoom.objects.order_by("-id")
        return render(request, "admintemplates/adminroomlist.html", context)


class AdminRoomCreateView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        context["roomform"] = HotelRoomForm
        return render(request, "admintemplates/adminroomcreate.html", context)

    def post(self, request, *args, **kwargs):
        room_form = HotelRoomForm(request.POST, request.FILES)
        if room_form.is_valid():
            room = room_form.save()
        else:
            messages.error(request, "Something went wrong")
        return redirect("hbsapp:adminroomlist")