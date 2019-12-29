from django import forms
from django.contrib.admin import ModelAdmin

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import College, Thread, Comment


class CollegeForm(forms.ModelForm):
    class Meta:
        model = College
        fields = (
            'country',
            'state',
            'full_name',
            'short_name',
            'parent_school',
        )


class CollegeAdmin(ModelAdmin):
    form = CollegeForm


class ThreadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ThreadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'threadForm'
        self.helper.form_class = 'createForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_thread'
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Thread
        fields = (
            'title',
            'body',
        )
    
    title = forms.CharField()
    body = forms.CharField(widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
