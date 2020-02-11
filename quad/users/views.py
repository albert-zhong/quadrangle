from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic.edit import CreateView

from colleges.messages import alert
from .models import MyUser
from .forms import MyUserCreationForm
from .tokens import account_activation_token


class SignUpView(CreateView):
    form_class = MyUserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.college = form.college
        # Set to true for now
        user.is_active = True
        user.save()

        # ignore email verification for now
        """
        mail_subject = 'Activate your Quadrangle.me account'
        message = render_to_string(
            'registration/activate_email.html',
            {
                'user': user,
                'domain': get_current_site(self.request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            }
        )
        to_email = form.cleaned_data['email']
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        alert(self.request, 'Please check your email to finish setting up your account.', 'success')
        """


        return super().form_valid(form)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        alert(request, 'Email successfully verified! You may now login.', 'success')
        return redirect('login')

    template_name = 'registration/activate.html'
    context = {'message': 'Incorrect validation link.'}

    return render(request, template_name, context)
