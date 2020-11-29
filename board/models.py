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
    status = models.ForeignKey(Board, related_name="status", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Task(TrackableDate):
    task = models.ManyToManyField(Status, through='CurrentStatusOfTask')
    name = models.CharField(max_length=200)
    desc = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class CurrentStatusOfTask(models.Model):
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    current_status = models.IntegerField()