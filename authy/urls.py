from django.urls import path
from authy.views import UserProfile, PasswordChangeDone, UserSearch
from .views import SignupView, CustomPasswordChangeView, EditProfileView
from django.contrib.auth import views as authViews 



urlpatterns = [
   	
    path('profile/edit', EditProfileView.as_view(), name='edit-profile'),
   	path('signup/', SignupView.as_view(), name='signup'),
   	path('login/', authViews.LoginView.as_view(template_name='login.html'), name='login'),
   	path('logout/', authViews.LogoutView.as_view(), {'next_page' : 'index'}, name='logout'),
   	path('changepassword/', CustomPasswordChangeView.as_view(), name='change_password'),
   	path('changepassword/done', PasswordChangeDone, name='change_password_done'),
   	path('passwordreset/', authViews.PasswordResetView.as_view(), name='password_reset'),
   	path('passwordreset/done', authViews.PasswordResetDoneView.as_view(), name='password_reset_done'),
   	path('passwordreset/<uidb64>/<token>/', authViews.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
   	path('passwordreset/complete/', authViews.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
	path('search/', UserSearch.as_view(), name='search-user')

]