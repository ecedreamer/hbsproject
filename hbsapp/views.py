from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View
from django.contrib import messages
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
        return redirect("hbsapp:clienthome")


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


class CustomerRoomBookingView(CustomerRequiredMixin, ClientMixin, View):
    pass


class CustomerProfileView(CustomerRequiredMixin, ClientMixin, View):
    def get(self, request, *args, **kwargs):
        context = self.context
        return render(request, "clienttemplates/customerprofile.html", context)

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
