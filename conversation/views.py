from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, get_user_model, get_user
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.shortcuts import redirect, get_object_or_404
from models import Message, Thread
from django.db.models import Q


def home(request):
    if request.user.is_authenticated():
        # If user is not authenticated, he can not access home page
        return render(request, 'conversation/home.html')
    return redirect(index)


@csrf_protect
def login_user(request):
    if request.user.is_authenticated():
        return redirect(home)
    state = "Please log in below..."
    email = password = ''
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(email=email, password=password)
        # User authentication using email and password
        if user is not None:
            if user.is_active:
                login(request, user)
                state = "You're successfully logged in!"
                return redirect(home)
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your email and/or password were incorrect."
    return render_to_response('conversation/login_form.html',{'state':state, 'email': email}, context_instance = RequestContext(request))


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/conversation/')


@csrf_protect
def signup(request):
    if request.user.is_authenticated():
        return redirect(home)
    state = "Please fill sign up details below..."
    email = password = ''
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password1')
        password_check = request.POST.get('password2')

        if password and password_check and password != password_check:
            state = "Passwords don't match"
        else:
            # Create a new user with provided email and password and redirect to login page on successful registration
            model = get_user_model()
            user = model.objects.create_user(email=email, password=password)
            state = "You're successfully registered!"
            return redirect(login_user)
    return render_to_response('conversation/signup_form.html', {'state': state},
                              context_instance=RequestContext(request))


def index(request):
    if request.user.is_authenticated():
        return redirect(home)
    # If user already signed in, redirect to home page
    return render_to_response('conversation/index.html')


def new_message(request):
    if request.user.is_anonymous():
        return redirect(index)
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


def view_message(request, message_id):
    if request.user.is_anonymous():
        return redirect(index)
    message = get_object_or_404(Message, id=message_id)
    # Find existing message in database through provided message-id
    # Raise 404 error in case message object is not found
    sender = message.sender
    content = message.content
    thread = message.thread
    return render(request, 'conversation/view_message.html', {'sender': sender, 'content': content, 'thread': thread})


def list_message(request, thread_id):
    if request.user.is_anonymous():
        return redirect(index)
    thread = get_object_or_404(Thread, id=thread_id)
    messages = Message.objects.filter(Q(thread=thread)).order_by('-timestamp').distinct()
    participants = thread.participants.all()
    return render(request, 'conversation/list_message.html', {'messages': messages, 'thread': thread,
                                                              'participants': participants})


def list_thread(request):
    if request.user.is_anonymous():
        return redirect(index)
    user = request.user
    threads = Thread.objects.filter(Q(participants=user))
    # Find all threads user is a participant of and display most recent message of each such thread
    messages = Message.objects.none()
    for thread in threads:
        thread_message = (thread.included_messages.order_by('-timestamp').values('id')[:1])
        message = Message.objects.filter(id=thread_message)
        messages = messages | message
    return render(request, 'conversation/list_thread.html', {'messages': messages})


def reply(request, thread_id):
    if request.user.is_anonymous():
        return redirect(index)
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