from django.urls import path
from direct.views import (NewConversationView, SendDirectView,
                          DirectsView, InboxView, UserSearchView)
urlpatterns = [
   	path('', InboxView.as_view(), name='inbox'),
   	path('directs/<username>', DirectsView.as_view(), name='directs'),
   	path('new/', UserSearchView.as_view(), name='usersearch'),
   	path('new/<username>', NewConversationView.as_view(), name='newconversation'),
   	path('send/', SendDirectView.as_view(), name='send_direct'),

]