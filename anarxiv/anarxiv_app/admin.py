from django.contrib import admin
from anarxiv_app.models import User, Paper, Post

admin.site.register(User)
admin.site.register(Paper)
admin.site.register(Post)
