from todo.views import TaskGroupViewSet, TaskViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)

router.register(r'task_groups', TaskGroupViewSet, basename='task_group')

router.register(r'task_groups/(?P<group_id>[0-9]+)/tasks', TaskViewSet, basename='task')

urlpatterns = router.urls
