from django.shortcuts import render, redirect
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from direct.models import Message


from django.db.models import Q
from django.core.paginator import Paginator

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
# Create your views here.


class InboxView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'  # Set the login URL as per your project's URL configuration
    template_name = 'direct/direct.html'  # Set the template name as per your project's file structure
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages = Message.get_messages(user=self.request.user)
        active_direct = None
        directs = None

        if messages:
            message = messages[0]
            active_direct = message['user'].username
            directs = Message.objects.filter(user=self.request.user, recipient=message['user'])
            directs.update(is_read=True)
            for message in messages:
                if message['user'].username == active_direct:
                    message['unread'] = 0
        
        context['directs'] = directs
        context['messages'] = messages
        context['active_direct'] = active_direct
        return context

class UserSearchView(LoginRequiredMixin, ListView):
    template_name = 'direct/search_user.html'
    context_object_name = 'users'
    paginate_by = 6

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return User.objects.filter(Q(username__icontains=query))
        return User.objects.none()

class DirectsView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'  # Set the login URL as per your project's URL configuration
    template_name = 'direct/direct.html'  # Set the template name as per your project's file structure
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        username = self.kwargs.get('username')
        messages = Message.get_messages(user=user)
        active_direct = username
        directs = Message.objects.filter(user=user, recipient__username=username)
        directs.update(is_read=True)
        for message in messages:
            if message['user'].username == username:
                message['unread'] = 0
        
        context['directs'] = directs
        context['messages'] = messages
        context['active_direct'] = active_direct
        return context
	
class NewConversationView(LoginRequiredMixin, View):
    login_url = '/login/'  # Set the login URL as per your project's URL configuration
    
    def get(self, request, username):
        from_user = request.user
        body = ''
        try:
            to_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect('usersearch')
        
        if from_user != to_user:
            Message.send_message(from_user, to_user, body)
        
        return redirect('inbox')

class SendDirectView(LoginRequiredMixin, View):
    login_url = '/login/'  # Set the login URL as per your project's URL configuration
    
    def post(self, request):
        from_user = request.user
        to_user_username = request.POST.get('to_user')
        body = request.POST.get('body')
        
        if to_user_username and body:  # Ensure both to_user and body are provided
            try:
                to_user = User.objects.get(username=to_user_username)
            except User.DoesNotExist:
                return HttpResponseBadRequest("User does not exist")
            
            Message.send_message(from_user, to_user, body)
            return redirect('inbox')
        else:
            return HttpResponseBadRequest("Invalid request")





	