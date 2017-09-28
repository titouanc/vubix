from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count

from .models import Selection, MyUser, Course


class SelectionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SelectionForm, self).__init__(*args, **kwargs)
        qs = Course.objects.annotate(scheds=Count('schedule')).exclude(scheds=0)
        self.fields['courses'].queryset = qs

    class Meta:
        model = Selection
        fields = ['courses', 'name']


class MyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = MyUser
