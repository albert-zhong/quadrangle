from django.contrib import admin
from .forms import CollegeAdmin
from .models import College, Thread, Comment, ThreadVote, CommentVote


admin.site.register(College, CollegeAdmin)
admin.site.register(Thread)
admin.site.register(Comment)
admin.site.register(ThreadVote)
admin.site.register(CommentVote)