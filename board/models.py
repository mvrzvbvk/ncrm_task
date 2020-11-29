from django.db import models

from user.models import User


class TrackableDate(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
        
    class Meta:
        abstract = True


class Board(TrackableDate):
    board_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Status(TrackableDate):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    priority = models.IntegerField(default=0, unique=True)

    def __str__(self):
        return self.name


class Task(TrackableDate):
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    desc = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name