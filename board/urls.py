from django.urls import path

from .views import (
    BoardList, BoardDetail, StatusList, StatusDetail, TaskList
)

app_name = "board"

urlpatterns = [
    path('boards/', BoardList.as_view(), name='create-or-get-boards'),
    path('boards/<int:id>/', BoardDetail.as_view(), name='get-board'),
    path('boards/<int:id>/status', StatusList.as_view(), name='create-or-get-boards'),
    path('boards/<int:id>/status/<int:status_id>', StatusDetail.as_view(), name='get-status'),
    path('tasks/', TaskList.as_view(), name='create-or-get-task'),
]
