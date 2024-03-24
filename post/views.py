from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from post.models import Stream, Post, Tag, Likes, PostFileContent
from post.forms import NewPostForm
from stories.models import Story, StoryStream

from comment.models import Comment
from comment.forms import CommentForm

from django.urls import reverse
from authy.models import Profile

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, FormView
from django.views import View

class IndexView(LoginRequiredMixin, ListView):
    template_name = 'index.html'
    context_object_name = 'post_items'
    queryset = Post.objects.none()  # Empty initial queryset

    def get_queryset(self):
        user = self.request.user
        posts = Stream.objects.filter(user=user)
        group_ids = [post.post_id for post in posts]
        return Post.objects.filter(id__in=group_ids).order_by('-posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['stories'] = StoryStream.objects.filter(user=user)
        return context
	
class NewPostView(LoginRequiredMixin, FormView):
    template_name = 'newpost.html'
    form_class = NewPostForm
    success_url = '/post'

    def form_valid(self, form):
        user = self.request.user
        tags_objs = []
        files_objs = []

        files = self.request.FILES.getlist('content')
        caption = form.cleaned_data.get('caption')
        tags_form = form.cleaned_data.get('tags')

        tags_list = list(tags_form.split(','))

        for tag in tags_list:
            t, created = Tag.objects.get_or_create(title=tag)
            tags_objs.append(t)

        for file in files:
            file_instance = PostFileContent(file=file, user=user)
            file_instance.save()
            files_objs.append(file_instance)

        p, created = Post.objects.get_or_create(caption=caption, user=user)
        p.tags.set(tags_objs)
        p.content.set(files_objs)
        p.save()
        return super().form_valid(form)

class PostDetailsView(LoginRequiredMixin, View):
    template_name = 'post_detail.html'
    comment_form_class = CommentForm

    def get_context_data(self, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = self.request.user
        profile = get_object_or_404(Profile, user=user)
        favorited = profile.favorites.filter(id=post_id).exists() if user.is_authenticated else False
        comments = Comment.objects.filter(post=post).order_by('date')
        return {
            'post': post,
            'favorited': favorited,
            'profile': profile,
            'form': self.comment_form_class(),
            'comments': comments,
        }

    def get(self, request, post_id):
        context = self.get_context_data(post_id)
        return render(request, self.template_name, context)

    def post(self, request, post_id):
        form = self.comment_form_class(request.POST)
        if form.is_valid():
            post = get_object_or_404(Post, id=post_id)
            user = self.request.user
            profile = get_object_or_404(Profile, user=user)
            comment = form.save(commit=False)
            comment.post = post
            comment.user = user
            comment.save()
            return HttpResponseRedirect(reverse('postdetails', args=[post_id]))
        else:
            context = self.get_context_data(post_id)
            context['form'] = form
            return render(request, self.template_name, context)

class TagsView(LoginRequiredMixin, View):
    def get(self, request, tag_slug):
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = Post.objects.filter(tags=tag).order_by('-posted')
        context = {
            'posts': posts,
            'tag': tag,
        }
        template = loader.get_template('tag.html')
        return HttpResponse(template.render(context, request))

class LikeView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        user = request.user
        post = get_object_or_404(Post, id=post_id)
        current_likes = post.likes
        liked = Likes.objects.filter(user=user, post=post).count()

        if not liked:
            like = Likes.objects.create(user=user, post=post)
            current_likes += 1
        else:
            Likes.objects.filter(user=user, post=post).delete()
            current_likes -= 1

        post.likes = current_likes
        post.save()

        return HttpResponseRedirect(reverse('postdetails', args=[post_id]))
    
class FavoriteView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        user = request.user
        post = get_object_or_404(Post, id=post_id)
        profile = get_object_or_404(Profile, user=user)

        if profile.favorites.filter(id=post_id).exists():
            profile.favorites.remove(post)
        else:
            profile.favorites.add(post)

        return HttpResponseRedirect(reverse('postdetails', args=[post_id]))

