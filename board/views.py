from django.shortcuts import render
from django.db import transaction

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
)
from rest_framework.generics import get_object_or_404

from .models import Board, Status, Task
from .serializers import BoardSerializer, StatusSerializer, TaskSerializer
from permissions import IsManagerUser
#TODO
#Create board only for manager user
#Create,update,delete status only for manager user
#Create task only for manager user
#Update status of task only for basic user


# def update_request(request, params: dict):
#     request.data._mutable = True
#     for param in params.keys():
#         request.data[param] = params[param]
#     request.data._mutable = False
#     return request



class BoardList(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    #permission_classes = [permissions.IsAuthenticated, IsManagerUser]
    queryset = Board.objects.all()

    def post(self, request):
        user = request.user
        name = request.data.get('name')
        with transaction.atomic():
            board = Board.objects.create(board_owner=user, name=name)
            board.save()
        return Response({"message": "Added board"}, status=HTTP_200_OK)

class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BoardSerializer
    #permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def put(self, request):
        user = request.user
        name = request.data.get('name')
        board = Board.objects.get(id=self.kwargs.get('id'))
        with transaction.atomic():
            board = Board.objects.create(board_owner=user, name=name)
            board.save()
        return Response({"message": "Updated board"}, status=HTTP_200_OK)

    def get_queryset(self):
        return Board.objects.filter(id=self.kwargs.get('id'))


class StatusList(generics.ListCreateAPIView):
    serializer_class = StatusSerializer
    #permission_classes = [permissions.IsAuthenticated, IsManagerUser]
    queryset = Status.objects.all()

    def post(self, request, id, status_id=None):
        #user = request.user
        name = request.data.get('name')
        #priority = request.data.get('priority')
        status = get_object_or_404(Board, id=id)
        with transaction.atomic():
            st = Status.objects.create(status=status, name=name)
            st.save()
        return Response({"message": "Added status"}, status=HTTP_200_OK)

class StatusDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StatusSerializer
    #permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'status_id'

    def get_queryset(self):
        return Status.objects.filter(id=self.kwargs.get('status_id'))


class TaskList(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    #permission_classes = [permissions.IsAuthenticated, IsManagerUser]
    queryset = Task.objects.all()

    def post(self, request, id, status_id=None):
        #user = request.user
        name = request.data.get('name')
        desc = request.data.get('desc')
        with transaction.atomic():
            task = Task.objects.create(name=name, desc=desc )
            task.save()
        return Response({"message": "Added task"}, status=HTTP_200_OK)

class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    #permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'status_id'

    def get_queryset(self):
        return Status.objects.filter(id=self.kwargs.get('status_id'))