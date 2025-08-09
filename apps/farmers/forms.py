from django import forms
from apps.marketplace.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["title", "price", "description", "image", "active"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "search-bar", "placeholder": "Title"}),
            "price": forms.NumberInput(attrs={"class": "search-bar", "step": "0.01", "min": "0"}),
            "description": forms.Textarea(attrs={"class": "search-bar", "rows": 4, "placeholder": "Description"}),
            "active": forms.CheckboxInput(),
        }
