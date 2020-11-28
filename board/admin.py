from django.contrib import admin

from .models import Board, Status, Task


admin.site.register(Board)
admin.site.register(Status)
admin.site.register(Task)


