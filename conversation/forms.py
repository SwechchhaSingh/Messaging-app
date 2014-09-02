from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from models import *
from django.contrib.auth import authenticate, login
from django.db.models import Q


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


class ReplyForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ['content']


class NewMessageForm(forms.ModelForm):

    # participants = forms.MultipleChoiceField()

    class Meta:
        model = Message
        fields = ['content']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(NewMessageForm, self).__init__(*args, **kwargs)
        self.fields['participants'] = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=MyUser.objects.all()
                                                                .exclude(email=self.request.user)
                                                                .values_list('id', 'email'))

    def save(self, commit=True):
        message = super(NewMessageForm, self).save(commit=False)
        message.sender = self.request.user
        # participants include all receivers and the message sender
        participants = MyUser.objects.filter(Q(id__in=self.cleaned_data.get('participants')) | Q(email=message.sender))
        thread = Thread.objects.create()
        thread.participants = participants
        # participants are to be saved in thread object
        thread.save()
        message.thread = thread
        if commit:
            message.save()
        return message