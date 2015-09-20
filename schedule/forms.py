from django.forms import ModelForm
from .models import Selection


class SelectionForm(ModelForm):
    class Meta:
        model = Selection
        fields = ['courses', 'name']