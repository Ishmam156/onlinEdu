from django import forms
from django.forms import ModelForm
from .models import User, CLASS_CHOICES, Course

# Course Choice form
class ChoiceForm(forms.ModelForm):
    options = forms.MultipleChoiceField(required=False, widget=forms.SelectMultiple(attrs={'class': "form-control"}), 
                                        choices=CLASS_CHOICES, label='')

    class Meta:
        model = User
        fields = ('options',)

# Course Type form
class TypeForm(forms.ModelForm):
    option = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), 
                                        choices=CLASS_CHOICES, label='')

    class Meta:
        model = Course
        fields = ('option',)


# Image Upload Form
class ImageUploadForm(forms.Form):
    thumbnail = forms.ImageField(label='', )