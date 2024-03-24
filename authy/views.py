from django.shortcuts import render, redirect, get_object_or_404
from authy.forms import SignupForm, ChangePasswordForm, EditProfileForm
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from authy.models import Profile
from post.models import Post, Follow, Stream
from django.db import transaction
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from django.core.paginator import Paginator

from django.urls import resolve
from django.db.models import Q


from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DetailView, ListView, View

def UserProfile(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)
	url_name = resolve(request.path).url_name
	
	if url_name == 'profile':
		posts = Post.objects.filter(user=user).order_by('-posted')

	else:
		posts = profile.favorites.all()

	#Profile info box
	posts_count = Post.objects.filter(user=user).count()
	following_count = Follow.objects.filter(follower=user).count()
	followers_count = Follow.objects.filter(following=user).count()

	#follow status
	follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

	#Pagination
	paginator = Paginator(posts, 8)
	page_number = request.GET.get('page')
	posts_paginator = paginator.get_page(page_number)

	template = loader.get_template('profile.html')

	context = {
		'posts': posts_paginator,
		'profile':profile,
		'following_count':following_count,
		'followers_count':followers_count,
		'posts_count':posts_count,
		'follow_status':follow_status,
		'url_name':url_name,
	}

	return HttpResponse(template.render(context, request))

class UserProfileView(DetailView):
    model = User
    template_name = 'profile.html'
    context_object_name = 'profile'
    slug_url_kwarg = "username"
    slug_field = "username"

    def get_object(self, queryset=None):
        username = self.kwargs.get(self.slug_url_kwarg)
        return get_object_or_404(self.model, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        url_name = resolve(self.request.path).url_name
        
        if url_name == 'profile':
            posts = Post.objects.filter(user=user).order_by('-posted')
        else:
            profile = self.object.profile
            posts = profile.favorites.all()

        # Profile info box
        posts_count = Post.objects.filter(user=user).count()
        following_count = Follow.objects.filter(follower=user).count()
        followers_count = Follow.objects.filter(following=user).count()

        # Follow status
        follow_status = Follow.objects.filter(following=user, follower=self.request.user).exists()

        # Pagination
        paginator = Paginator(posts, 8)
        page_number = self.request.GET.get('page')
        posts_paginator = paginator.get_page(page_number)

        context.update({
            'posts': posts_paginator,
            'following_count': following_count,
            'followers_count': followers_count,
            'posts_count': posts_count,
            'follow_status': follow_status,
            'url_name': url_name,
        })
        return context


def UserProfileFavorites(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)
	
	posts = profile.favorites.all()

	#Profile info box
	posts_count = Post.objects.filter(user=user).count()
	following_count = Follow.objects.filter(follower=user).count()
	followers_count = Follow.objects.filter(following=user).count()

	#Pagination
	paginator = Paginator(posts, 8)
	page_number = request.GET.get('page')
	posts_paginator = paginator.get_page(page_number)

	template = loader.get_template('profile_favorite.html')

	context = {
		'posts': posts_paginator,
		'profile':profile,
		'following_count':following_count,
		'followers_count':followers_count,
		'posts_count':posts_count,
	}

	return HttpResponse(template.render(context, request))


class SignupView(CreateView):
    template_name = 'signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs) 

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        form.instance.username = username
        form.instance.email = email
        form.instance.set_password(password)
        return super().form_valid(form)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = ChangePasswordForm
    template_name = 'change_password.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        # Update the user's password
        new_password = form.cleaned_data['new_password']
        self.request.user.set_password(new_password)
        self.request.user.save()

        # Update the session auth hash to prevent the user from being logged out
        update_session_auth_hash(self.request, self.request.user)

        # Call the parent class's form_valid method to handle the rest
        return super().form_valid(form)


def PasswordChangeDone(request):
	return render(request, 'change_password_done.html')

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = EditProfileForm
    template_name = 'edit_profile.html'
    success_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        response = super().form_valid(form)
        # Additional logic if needed
        return response

class FollowView(LoginRequiredMixin, View):

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, username, option):
        following = get_object_or_404(User, username=username)

        try:
            f, created = Follow.objects.get_or_create(follower=request.user, following=following)

            if int(option) == 0:
                f.delete()
                Stream.objects.filter(following=following, user=request.user).all().delete()
            else:
                posts = Post.objects.all().filter(user=following)[:25]

                with transaction.atomic():
                    for post in posts:
                        stream = Stream(post=post, user=request.user, date=post.posted, following=following)
                        stream.save()

            return HttpResponseRedirect(reverse('profile', args=[username]))
        except User.DoesNotExist:
            return HttpResponseRedirect(reverse('profile', args=[username]))

class UserSearch(LoginRequiredMixin, ListView):
    template_name = 'follow_search.html'
    context_object_name = 'users'
    paginate_by = 6

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return User.objects.filter(Q(username__icontains=query))
        return User.objects.none()


