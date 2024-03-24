from django.urls import path
from notifications.views import ShowNotificationsView,  DeleteNotificationView


urlpatterns = [
   	path('', ShowNotificationsView.as_view(), name='show-notifications'),
   	path('<pk>/delete', DeleteNotificationView.as_view(), name='delete-notification'),

]