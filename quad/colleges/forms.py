from django import forms
from django.contrib.admin import ModelAdmin

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import College, Thread, Comment


class CollegeForm(forms.ModelForm):
    class Meta:
        model = College
        fields = [
            'full_name',
            'short_name',
            'logo',
            'banner',
        ]


class CollegeAdmin(ModelAdmin):
    form = CollegeForm


class ThreadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ThreadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'threadForm'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Thread
        fields = [
            'title',
            'body',
            'is_anonymous',
        ]
    
    body = forms.CharField(widget=forms.Textarea)


# Removes 'is_anonymous' field
class ThreadEditForm(ThreadForm):
    class Meta:
        model = Thread
        fields = [
            'title',
            'body',
        ]


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'commentForm'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Comment
        fields = (
            'body',
            'is_anonymous',
        )

    body = forms.CharField(widget=forms.Textarea)


# Removes 'is_anonymous' field
class CommentEditForm(CommentForm):
    class Meta:
        model = Comment
        fields = ['body']    
