from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from models import Message, Thread, MyUser
from django.db.models import Q
from django.views.generic import FormView, RedirectView, DetailView, ListView, TemplateView
from forms import CustomUserCreationForm, CustomAuthenticationForm, NewMessageForm, ReplyForm


class LoginView(FormView):
    template_name = 'conversation/login_form.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('list_thread')

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
    success_url = reverse_lazy('list_thread')

    def form_valid(self, form):
        user = form.save()
        return super(SignupView, self).form_valid(form)


class IndexView(TemplateView):
    template_name = 'conversation/index.html'


class MessageDetailView(DetailView):
    # To view details of individual message
    model = Message
    template_name = 'conversation/view_message.html'


class ListMessageView(ListView):
    queryset = {}  # Including custom queries in context, so queryset is not required
    template_name = 'conversation/list_message.html'

    # Customising context data
    def get_context_data(self, **kwargs):
        context = super(ListMessageView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        thread = get_object_or_404(Thread, id=pk)
        context['participants'] = thread.participants.all()
        context['thread'] = thread
        return context

    def get_queryset(self):
        pk = self.kwargs['pk']
        thread = get_object_or_404(Thread, id=pk)
        messages_list = Message.objects.filter(Q(thread=thread)).order_by('-timestamp').distinct()
        # Messages included in the current thread only
        return messages_list


class ListThreadView(ListView):
    queryset = {}  # Including custom queries in context, so queryset is not required
    template_name = 'conversation/list_thread.html'

    def get_queryset(self):
        user = MyUser.objects.filter(email=self.request.user)
        threads = Thread.objects.filter(Q(participants=user))
        # Find all threads user is a participant of and display most recent message of each such thread
        messages = Message.objects.none()
        for thread in threads:
            thread_message = (thread.included_messages.order_by('-timestamp').values('id')[:1])
            #Include one (most recent) message of each thread user is a participant of
            message = Message.objects.filter(id=thread_message)
            messages = messages | message
        messages_list = messages.order_by('-timestamp')
        return messages_list

class ReplyView(FormView):
    # Adding reply message to old thread
    template_name = 'conversation/reply.html'
    form_class = ReplyForm

    def get_success_url(self):
        return reverse_lazy('list_message', kwargs={'pk': self.kwargs['pk'], })

    # Customising context data
    def get_context_data(self, **kwargs):
        context = super(ReplyView, self).get_context_data(**kwargs)
        context['thread'] = Thread.objects.get(id=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        message = form.save(commit=False)
        message.sender = self.request.user
        message.thread_id = self.kwargs['pk']
        message.save()
        return super(ReplyView, self).form_valid(form)


class NewMessageView(FormView):
    # New thread creation for new message
    # Requires participants for thread
    template_name = 'conversation/new_message.html'
    form_class = NewMessageForm

    def get_success_url(self):
        return reverse_lazy('list_message', kwargs={'pk': self.kwargs['pk'], })

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(NewMessageView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        message = form.save()
        self.kwargs['pk'] = message.thread_id
        return super(NewMessageView, self).form_valid(form)