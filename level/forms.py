# forms.py
from django import forms
from .models import CustomUser

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'age', 'height', 'weight']

    # กำหนดข้อกำหนดหรือ validation เพิ่มเติม
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 0 or age > 120:
            raise forms.ValidationError("Please enter a valid age.")
        return age
