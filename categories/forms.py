# forms.py
from django import forms
from .models import Purchase

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['fullname', 'size', 'phone', 'address', 'landmark', 'pincode']
