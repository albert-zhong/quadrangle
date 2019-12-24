from django.contrib import admin
from .forms import CollegeAdmin
from .models import College, Thread, Comment


admin.site.register(College, CollegeAdmin)
admin.site.register(Thread)
admin.site.register(Comment)