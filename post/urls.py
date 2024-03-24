from django.urls import path
from post.views import IndexView, NewPostView, PostDetailsView, TagsView, LikeView, favorite


urlpatterns = [
   	path('', IndexView.as_view(), name='index'),
   	path('newpost/', NewPostView.as_view(), name='newpost'),
   	path('<uuid:post_id>', PostDetailsView.as_view(), name='postdetails'),
   	path('<uuid:post_id>/like', LikeView.as_view(), name='postlike'),
   	path('<uuid:post_id>/favorite', favorite, name='postfavorite'),
   	path('tag/<slug:tag_slug>', TagsView.as_view(), name='tags'),
]