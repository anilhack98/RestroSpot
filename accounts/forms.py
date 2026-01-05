from django import forms
from .models import User,UserProfile
from .validators import allow_only_images_validator

class UserForm(forms.ModelForm):
    address=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'start typing...','required':'required'}))
    password=forms.CharField(widget=forms.PasswordInput())
    confirm_password=forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model=User
        fields=['first_name','last_name','username','email','password']

        
    # Custom validation for password matching
    def clean(self):
        cleaned_data=super(UserForm,self).clean()
        # Get password values
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')

         # Check if passwords match
        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match"
            )
        

 # USER PROFILE FORM       
class UserProfileForm(forms.ModelForm):
    # Profile picture field with image validation
    profile_picture=forms.ImageField(widget=forms.FileInput(attrs={'class':'btn btn-info'}),validators=[allow_only_images_validator])
    # Cover photo field with image validation
    cover_photo=forms.ImageField(widget=forms.FileInput(attrs={'class':'btn btn-info'}),validators=[allow_only_images_validator])

    # latitude=forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    # longitude=forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    class Meta:
        model=UserProfile
        # Fields taken from UserProfile model
        fields=['profile_picture','cover_photo','address','country','state','city','pin_code','latitude','longitude']

        