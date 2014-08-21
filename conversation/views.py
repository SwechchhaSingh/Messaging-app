from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, get_user_model, get_user
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.shortcuts import redirect
from conversation.models import Message
from django.db.models import Q


def home(request):
    if request.user.is_authenticated():
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

        if user is not None:
            if user.is_active:
                login(request, user)
                state = "You're successfully logged in!"
                return  redirect(home)
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
            model=get_user_model()
            user = model.objects.create_user(email=email, password=password)
            state = "You're successfully registered!"
            return redirect(login_user)
    return render_to_response('conversation/signup_form.html', {'state': state}, context_instance = RequestContext(request))


def index(request):
    if request.user.is_authenticated():
        return redirect(home)
    return render_to_response('conversation/index.html')


def new_message(request):
    if request.user.is_anonymous():
        return redirect(index)
    model = get_user_model()
    receivers = model.objects.all()
    sender = get_user(request)
    message = ''
    if request.POST:
        message = request.POST.get('message')
        receivers = request.POST.getlist('receivers')
        new_message = Message.objects.save(sender=sender, content=message, receiver_list=receivers)
        return redirect(home)

    return render_to_response('conversation/new_message.html', {'receivers': receivers},  context_instance= RequestContext(request))


def view_message(request, message_id):
    if request.user.is_anonymous():
        return redirect(index)
    message = Message.objects.get(id=message_id)
    sender = message.sender
    receivers = message.receiver.all()
    content = message.content
    return render(request, 'conversation/view_message.html', {'sender': sender, 'receivers': receivers, 'content': content})


def list_message(request):
    if request.user.is_anonymous():
        return redirect(index)
    user = get_user(request)
    messages = Message.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('-timestamp').distinct()
    return render(request, 'conversation/list_message.html',{'messages': messages})