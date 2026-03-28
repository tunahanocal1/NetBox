from django import forms
from .models import Profile
from .models import BookReview

class ReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ['rating', 'comment']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
