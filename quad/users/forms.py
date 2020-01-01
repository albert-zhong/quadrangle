from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from colleges.models import CollegeEmail
from .models import MyUser


class MyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = MyUser
        fields = [
            'email',
            'first_name',
            'last_name',
        ]

    def clean(self):
        email = self.cleaned_data['email']
        try:
            user = MyUser.objects.get(email=email)
            raise ValidationError('A user with this email already exists')
        except MyUser.DoesNotExist:
            pass

        domain = email.split('@')[1]
        try:
            college_email = CollegeEmail.objects.select_related('college').get(domain=domain)
            self.college = college_email.college
        except CollegeEmail.DoesNotExist:
            raise ValidationError('This email is not associated with any colleges.')

        return self.cleaned_data


class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = MyUser
        fields = ['email',]
