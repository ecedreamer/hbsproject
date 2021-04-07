from django import forms
from .models import *


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
        fields = ["total_persons", "estimated_arrival_time", "booking_for_in_days", "message", "payment_method"]
        widgets = {
            "total_persons": forms.NumberInput(attrs={
                "class": "form-control"
            }),
            "estimated_arrival_time": forms.DateTimeInput(attrs={
                "class": "form-control",
                "type": "datetime-local"
            }),
            "booking_for_in_days": forms.NumberInput(attrs={
                "class": "form-control"
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