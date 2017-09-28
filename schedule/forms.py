from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Selection, MyUser


class SelectionForm(ModelForm):
    class Meta:
        model = Selection
        fields = ['courses', 'name']

class MyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = MyUser