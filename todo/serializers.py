from rest_framework import serializers

from todo.models import TaskGroup, Task


class TaskGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskGroup
        fields = '__all__'


# class TaskSerializer(serializers.ModelSerializer):
#     group_id = serializers.IntegerField(write_only=True)
#
#     class Meta:
#         model = Task
#         exclude = (
#             'group',
#         )

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
