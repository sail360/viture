from django import forms
from django.contrib.auth.forms import UserCreationForm
from .settings import SIGNUP_SECRET_PASSCODE
class LocalizationUploadForm(forms.Form):
    query_image = forms.ImageField(label="Upload query image")

class VRSUploadForm(forms.Form):
    vrs_file = forms.FileField(
        label="VRS file",
        widget=forms.ClearableFileInput(attrs={"accept": ".vrs"})
    )
    json_file = forms.FileField(
        label="JSON file",
        widget=forms.ClearableFileInput(attrs={"accept": ".json,application/json"})
    )

    def clean(self):
        cleaned_data = super().clean()
        vrs_file = cleaned_data.get("vrs_file")
        json_file = cleaned_data.get("json_file")

        if not vrs_file or not json_file:
            return cleaned_data

        vrs_name = vrs_file.name
        json_name = json_file.name

        if not vrs_name.lower().endswith(".vrs"):
            raise forms.ValidationError("The VRS file must have a .vrs extension.")

        expected_json_name = f"{vrs_name}.json"
        if json_name != expected_json_name:
            raise forms.ValidationError(
                f'The JSON filename must exactly match "{expected_json_name}".'
            )

        return cleaned_data


class SignupForm(UserCreationForm):
    secret_passcode = forms.CharField(required=True)

    def clean_secret_passcode(self):
        value = self.cleaned_data["secret_passcode"]
        if value != SIGNUP_SECRET_PASSCODE:
            raise forms.ValidationError("Invalid secret passcode.")
        return value

    def clean_password1(self):
        password = self.cleaned_data.get("password1", "")

        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        # if not re.search(r"[a-z]", password):
        #     raise forms.ValidationError("Password must contain a lowercase letter.")
        # if not re.search(r"[A-Z]", password):
        #     raise forms.ValidationError("Password must contain an uppercase letter.")
        # if not re.search(r"[^A-Za-z0-9]", password):
        #     raise forms.ValidationError("Password must contain a special character.")

        return password