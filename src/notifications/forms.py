from django import forms


class SubscriptionForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Введите Email"}),
        error_messages={"required": "Введите Email"},
    )
