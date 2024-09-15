# from django import forms
# from .models import Pet_Model

# class PostForm(forms.ModelForm):
#     class Meta:
#         model = Pet_Model
#         fields = '__all__'


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
from .models import Pet_Model

class PostForm(forms.ModelForm):
    class Meta:
        model = Pet_Model
        fields = '__all__'

    