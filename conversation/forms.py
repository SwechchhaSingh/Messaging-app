from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from models import *
from django.contrib.auth import authenticate, login, logout, get_user_model, get_user


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label="Email")

    class Meta:
        model = MyUser
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # remove username
        self.fields.pop('username')

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Override the default AuthenticationForm to force email-as-username behavior.
    """
    email = forms.EmailField(label="Email")

    def __init__(self, request=None, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CustomAuthenticationForm, self).__init__(request, *args, **kwargs)
        del self.fields['username']
        self.fields.keyOrder = ['email', 'password']

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is not None:
                if self.user_cache.is_active:
                    login(self.request, self.user_cache)
        return self.cleaned_data


class NewMessageForm(forms.Form):

    message = forms.CharField(widget=forms.Textarea)
    receivers = forms.MultipleChoiceField(required=True, widget=forms.SelectMultiple,
                                          choices=MyUser.objects.all().values_list('id', 'email'))
    # receivers = model.objects.exclude(email=request.user)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(NewMessageForm, self).__init__(*args, **kwargs)
        message = ''

    def clean(self):
        message = self.cleaned_data.get('message')
        receivers = self.cleaned_data.get('receivers')
        if message and receivers:
            participants = MyUser.objects.filter(id__in=receivers)
            sender = self.request.user
            new_message = Message.objects.save(sender=sender, content=message, receiver_list=participants)
        return self.cleaned_data

#
# class ReplyForm(forms.Form):
#
#     def __init__(self, *args, **kwargs):
#         self.request = kwargs.pop('request', None)
#         super(ReplyForm, self).__init__(*args, **kwargs)
#         message = ''
#
#     def clean(self):
#         message = self.cleaned_data.get('message')
#         print "------------------------------", self.request, "----------------------------------------"
#         if message:
#             sender = self.request.user
#             print sender, "__________________________________________________________________________"
#             new_message = Message.objects.reply(sender=sender, content=message, thread_id=thread_id)
#         return self.cleaned_data


class ReplyForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ['content']

#
# class NewMessageForm(forms.ModelForm):
#
#     class Meta:
#         model = Message
#         fields = ['content']
