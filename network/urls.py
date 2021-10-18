
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('posts', views.posts, name='posts'),
    path("addpost", views.addpost, name='addpost'),
    path('addlike/<int:id>', views.addlike, name='addlike'),
    path('likes', views.likes, name='likes'),
    path('profile/<str:name>', views.profile, name='profile'),
    path('follow/<str:name>/<int:boo>', views.follow, name='follow'),
    path('followed/<str:name>', views.followed, name='followed'),
    path('following', views.following, name='following'),
    path('posts/<int:ID>', views.getpost, name='getpost'),
    path('edit/<int:ID>', views.edit, name='edit'),
    path('getfollow/<str:name>', views.getfollow, name='getfollow'),

    path('auctions', views.auctions, name='auctions'),
    path("closed", views.closed, name='closed'),
    path('createlisting', views.createlisting, name="createlisting"),
    path("create", views.create, name='create'),
    path("listings/<int:name>", views.item, name='item'),
    path("bid/<int:name>", views.bid,name='bid'),
    path('watch', views.watch, name='watch'),
    path("watchlist/<int:name>", views.listwatch, name='listwatch'),
    path("removewatch/<int:name>", views.removewatch, name='removewatch'),
    path("comment/<int:name>", views.comment, name='comment'),
    path('categories', views.categories, name='categories'),
    path("viewbycategory/<str:name>", views.viewbycategory, name='viewbycategory'),
    path('endauction/<int:name>', views.endauction, name='endauction'),

    path('mail', views.mail, name='mail'),
    path("emails", views.compose, name="compose"),
    path("emails/<int:email_id>", views.email, name="email"),
    path("emails/<str:mailbox>", views.mailbox, name="mailbox"),
]
