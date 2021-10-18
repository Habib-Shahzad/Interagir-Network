from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Follow)

admin.site.register(Email)
admin.site.register(Bid)
admin.site.register(Listing)
admin.site.register(Watchlist)
admin.site.register(Comment)
admin.site.register(Category)