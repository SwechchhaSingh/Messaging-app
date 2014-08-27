from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, get_user_model, get_user
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import redirect, get_object_or_404
from models import Message, Thread
from django.db.models import Q
from django.views.generic import FormView, RedirectView, View
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.decorators import method_decorator
from forms import CustomUserCreationForm, CustomAuthenticationForm


@login_required
def home(request):
    return render(request, 'conversation/home.html')


# class HomeView(View):
#     template_name = 'conversation/home.html'


class LoginView(FormView):
    template_name = 'conversation/login_form.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('home')

     # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(LoginView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class LogoutView(RedirectView):
    """
    Provides users the ability to logout
    """
    url = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class SignupView(FormView):
    template_name = 'conversation/signup_form.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')


def index(request):
    if request.user.is_authenticated():
        return redirect(home)
    # If user already signed in, redirect to home page
    return render_to_response('conversation/index.html')


@login_required
def new_message(request):
    # New thread creation for new message
    # Requires participants for thread and initial message
    model = get_user_model()
    receivers = model.objects.exclude(email=request.user)
    sender = get_user(request)
    message = ''
    if request.POST:
        message = request.POST.get('message')
        receivers = request.POST.getlist('receivers')
        new_message = Message.objects.save(sender=sender, content=message, receiver_list=receivers)
        return redirect(home)

    return render_to_response('conversation/new_message.html', {'receivers': receivers},
                              context_instance=RequestContext(request))


@login_required
def view_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    # Find existing message in database through provided message-id
    # Raise 404 error in case message object is not found
    sender = message.sender
    content = message.content
    thread = message.thread
    return render(request, 'conversation/view_message.html', {'sender': sender, 'content': content, 'thread': thread})


@login_required
def list_message(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    messages = Message.objects.filter(Q(thread=thread)).order_by('-timestamp').distinct()
    # Messages included in the current thread only
    participants = thread.participants.all()
    return render(request, 'conversation/list_message.html', {'messages': messages, 'thread': thread,
                                                              'participants': participants})


@login_required
def list_thread(request):
    user = request.user
    threads = Thread.objects.filter(Q(participants=user))
    # Find all threads user is a participant of and display most recent message of each such thread
    messages = Message.objects.none()
    for thread in threads:
        thread_message = (thread.included_messages.order_by('-timestamp').values('id')[:1])
        #Include one (most recent) message of each thread user is a participant of
        message = Message.objects.filter(id=thread_message)
        messages = messages | message
    return render(request, 'conversation/list_thread.html', {'messages': messages})


@login_required
def reply(request, thread_id):
    sender = request.user
    message = ''
    thread = get_object_or_404(Thread, id=thread_id)
    # Reply to a thread requires thread and message content
    if request.POST:
        message = request.POST.get('message')
        new_message = Message.objects.reply(sender=sender, content=message, thread_id=thread_id)
        return redirect(list_message, thread_id=thread_id)

    return render_to_response('conversation/reply.html', {'thread': thread},
                              context_instance=RequestContext(request))