from rest_framework import viewsets
from rest_framework.response import Response

from todo.models import TaskGroup, Task
from todo.serializers import TaskGroupSerializer, TaskSerializer


class TaskGroupViewSet(viewsets.ModelViewSet):
    queryset = TaskGroup.objects.all()
    serializer_class = TaskGroupSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

# class TaskViewSet(viewsets.ViewSet):
#     def list(self, request, group_id):
#         task_group = TaskGroup.objects.get(pk=group_id)
#         tasks = task_group.tasks.all()
#         serializer = TaskSerializer(tasks, many=True)
#         return Response(serializer.data)
#
#     def retrieve(self, request, group_id, pk):
#         task_group = TaskGroup.objects.get(pk=group_id)
#         task = task_group.tasks.get(pk=pk)
#         serializer = TaskSerializer(task)
#         return Response(serializer.data)
#
#     def create(self, request, group_id):
#         data = request.data
#         serializer = TaskSerializer(data=data)
#         serializer.is_valid()
#         serializer.save()
#         return Response(serializer.data)
#
#     def update(self, request, group_id, pk):
#         task_group = TaskGroup.objects.get(pk=group_id)
#         task = task_group.tasks.get(pk=pk)
#         serializer = TaskSerializer(task, data=request.data)
#         serializer.is_valid()
#         serializer.save()
#         return Response(serializer.data)
#
#     def destroy(self, request, group_id, pk):
#         task_group = TaskGroup.objects.get(pk=group_id)
#         task = task_group.tasks.get(pk=pk)
#         task.delete()
#         return Response([])
