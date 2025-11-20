from django import forms
from shop.models import ReviewRating


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-600',
                'placeholder': 'Summary of your review'
            }),
            'review': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-600',
                'placeholder': 'Share your experience with this product',
                'rows': 4
            }),
            # Changed from Select to HiddenInput to accept Float values from JS
            'rating': forms.NumberInput(attrs={
                'id': 'rating_input', 
                'type': 'hidden', 
                'min': 1, 
                'max': 5, 
                'step': 0.5
            })
        }