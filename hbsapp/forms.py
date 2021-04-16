from django import forms
from .models import *


class ContactForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["full_name", "mobile", "email", "message"]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "mobile": forms.NumberInput(attrs={
                "class": "form-control",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "pattern": '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            })
        }

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "placeholder": "Enter your email...",
        "class": "form-control",
        "pattern": '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Enter your password...",
        "class": "form-control"
    }))

# customer forms
class CustomerRegistrationForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your first name..."
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your last name..."
    }))
    address = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your address..."
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "placeholder": "Enter your email...",
        "class": "form-control",
        "pattern": '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Enter your password...",
        "class": "form-control"
    }))
    mobile = forms.CharField(widget=forms.NumberInput(attrs={
        "placeholder": "Enter your email...",
        "class": "form-control",
    }))


class RoomBookingForm(forms.ModelForm):
    class Meta:
        model = RoomBooking
        fields = ["total_persons", "booking_starts", "booking_ends", "message", "payment_method"]
        widgets = {
            "total_persons": forms.NumberInput(attrs={
                "class": "form-control"
            }),
            "booking_starts": forms.DateTimeInput(attrs={
                "class": "form-control",
                "type": "date",
                "onchange": "compareDates()"
            }),
            "booking_ends": forms.DateTimeInput(attrs={
                "class": "form-control",
                "type": "date",
                "onchange": "compareDates()"
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
            "payment_method": forms.Select(attrs={
                "class": "form-control",
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_method"].empty_label = "Select payment method"
    


# admin forms

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ["name", "image", "address", "contact", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
    



class HotelRoomForm(forms.ModelForm):
    class Meta:
        model = HotelRoom
        fields = ["hotel", "room_type", "room_code", "image", "description", "price"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"