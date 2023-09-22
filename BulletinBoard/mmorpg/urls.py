from allauth.account.views import LoginView, LogoutView
from django.urls import path
from .views import PostList, PostDetail, ReplyDetail, ReplyList, PostCreate, ReplyCreate, PostDetailUser, PostUpdate, PostDelete, ReplyDelete, user_posts, user_replies, accept_reply


urlpatterns = [
   path('', PostList.as_view(), name='posts'),
   path('<int:pk>', PostDetail.as_view(), name='post'),
   path('replies/', ReplyList.as_view(), name='replies'),
   path('reply/<int:pk>/', ReplyDetail.as_view(), name='reply'),
   path('create/', PostCreate.as_view(), name='post_create'),
   path('<int:pk>/reply_create/', ReplyCreate.as_view(), name='reply_create'),
   path('post_user/<int:pk>/', PostDetailUser.as_view(), name='post_user'),
   path('update/<int:pk>', PostUpdate.as_view(), name='post_update'),
   path('delete/<int:pk>', PostDelete.as_view(), name='post_delete'),
   path('reply_delete/<int:pk>', ReplyDelete.as_view(), name='reply_delete'),
   path('user_posts/', user_posts, name='user_posts'),
   path('user_replies/', user_replies, name='user_replies'),
   path('accept_reply/<int:pk>/', accept_reply, name='accept_reply'),
]