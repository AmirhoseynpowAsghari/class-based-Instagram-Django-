from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views.generic.base import ContextMixin


from notifications.models import Notification

from django.views.generic import TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

# Create your views here.
class ShowNotificationsView(LoginRequiredMixin, TemplateView):
    template_name = 'notifications.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        notifications = Notification.objects.filter(user=user).order_by('-date')
        Notification.objects.filter(user=user, is_seen=False).update(is_seen=True)
        context['notifications'] = notifications
        return context
    
# class DeleteNotificationView(LoginRequiredMixin, DeleteView):
#     model = Notification
#     success_url = reverse_lazy('show-notifications')

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         return queryset.filter(user=self.request.user)
    
class DeleteNotificationView(LoginRequiredMixin, DeleteView):
    model = Notification
    success_url = reverse_lazy('show-notifications')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        # Get the notification instance to be deleted
        self.object = self.get_object()

        # Delete the notification instance
        self.object.delete()

        # Redirect back to the notifications page
        return HttpResponseRedirect(self.get_success_url())

class CountNotificationsMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        count_notifications = 0
        if self.request.user.is_authenticated:
            count_notifications = Notification.objects.filter(user=self.request.user, is_seen=False).count()
        context['count_notifications'] = count_notifications
        return context
    



