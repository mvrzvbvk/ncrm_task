import json

from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
)
from rest_framework.generics import get_object_or_404

from user.models import User
from .models import Board, Status, Task
from .serializers import BoardSerializer, StatusSerializer, TaskSerializer
from permissions import IsManagerUser
#TODO
#Create board only for manager user
#Create,update,delete status only for manager user
#Create task only for manager user
#Update status of task only for basic user

USER_BASIC = 0
USER_MANAGER = 1

class BoardList(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    #permission_classes = [permissions.IsAuthenticated, IsManagerUser]
    queryset = Board.objects.all()

    def post(self, request):
        user = request.user
        name = request.data.get('name')
        if user.user_type is USER_BASIC:
            return Response({"detail": "Permission denied!"}, status=HTTP_403_FORBIDDEN)
        with transaction.atomic():
            board = Board.objects.create(board_owner=user, name=name)
            board.save()
        return Response({"message": "Added board"}, status=HTTP_200_OK)

class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BoardSerializer
    #permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def patch(self, request, id, *args, **kwargs):
        user = request.user
        get_board = get_object_or_404(Board, id=id)
        owner_id = get_board.board.board_owner.id
        if user.id is not owner_id:
            return Response({"detail": "Permission denied!"}, status=HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(get_board, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return Board.objects.filter(id=self.kwargs.get('id'))


class StatusList(generics.ListCreateAPIView):
    serializer_class = StatusSerializer
    #permission_classes = [permissions.IsAuthenticated, IsManagerUser]
    #queryset = Status.objects.filter()

    def get_queryset(self):
        return Status.objects.filter(board=self.kwargs['id'])

    def post(self, request, id, status_id=None):
        user = request.user
        name = request.data.get('name')
        priority = request.data.get('priority')
        board = get_object_or_404(Board, id=id)
        if user.user_type is USER_BASIC:
            return Response({"detail": "Permission denied!"}, status=HTTP_403_FORBIDDEN)
        with transaction.atomic():
            st = Status.objects.create(board=board, name=name, priority=priority)
            st.save()
        return Response({"message": "Added status"}, status=HTTP_200_OK)

class StatusDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StatusSerializer
    #permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Status.objects.filter(id=self.kwargs.get('pk'), board=self.kwargs.get('id'))

    def patch(self, request, pk, *args, **kwargs):
        user = request.user
        status = get_object_or_404(Status, pk=pk)
        owner_id = status.board.board_owner.id
        if user.id is not owner_id:
            return Response({"detail": "Permission denied!"}, status=HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(status, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(self, request, pk, *args, **kwargs):
        user = request.user
        status = get_object_or_404(Status, pk=pk)
        task = Task.objects.filter(status=pk)
        owner_id = status.board.board_owner.id
        if task or user.id is not owner_id:
            return Response({"detail": "This status has tasks, you can't delete!"}, status=HTTP_403_FORBIDDEN)
        status.delete()
        return Response(status=HTTP_204_NO_CONTENT)
       

class TaskList(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    #permission_classes = [permissions.IsAuthenticated, IsManagerUser]
    queryset = Task.objects.all()

    def post(self, request):
        user = request.user
        name = request.data.get('name')
        desc = request.data.get('desc')
        username = request.data.get('username')
        assign_user = get_object_or_404(User, username=username)
        def_status = Status.objects.all().first()
        if user.user_type is USER_BASIC:
            return Response({"detail": "Permission denied!"}, status=HTTP_403_FORBIDDEN)
        with transaction.atomic():
            task = Task.objects.create(status=def_status, name=name, desc=desc, assigned_to=assign_user )
            task.save()
        return Response({"message": "Added task"}, status=HTTP_200_OK)

class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    #permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Task.objects.filter(id=self.kwargs.get('id'))


    def patch(self, request, id, *args, **kwargs):
        user = request.user
        task = get_object_or_404(Task, id=id)
        owner_id = task.status.board.board_owner.id
        if user.id is not owner_id:
            return Response({"detail": "Permission denied!"}, status=HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class ChangeStatusOfTask(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    #permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Task.objects.filter(id=self.kwargs.get('id'))

    def patch(self, request, id,  *args, **kwargs):
        user = request.user
        task = get_object_or_404(Task, id=id)
        status = request.data.get('status')
        n_priority = Status.objects.get(id=status)
        next_priority = n_priority.priority-1
        if user.user_type is not USER_BASIC or user.id is not task.assigned_to.id:
                return Response({"detail": "Permission denied!"}, status=HTTP_403_FORBIDDEN)
        if task.status.priority is not next_priority:
                return Response({"detail": "you must change the task status sequentially"}, status=HTTP_403_FORBIDDEN)
        task.status = n_priority
        task.save()
        return Response({"message": "Updated task"}, status=HTTP_200_OK)
    

#or user.id is not task.assigned_to.user.id