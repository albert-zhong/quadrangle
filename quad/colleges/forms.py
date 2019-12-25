from django import forms
from django.contrib.admin import ModelAdmin

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
    class Meta:
        model = Thread
        fields = (
            'title',
            'body',
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
