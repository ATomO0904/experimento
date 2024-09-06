from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_not_required


# Create your views here.

class SingUpView(CreateView):
    model= User
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'

    # def form_invalid(self, form: BaseModelForm) -> HttpResponse:
    #     user = form.save(commit=False)
    #     user.set_password('1234')
    #     user.save()
    #     return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('login') + '?register'