from rest_framework.decorators import api_view, authentication_classes
from myapp.models import Task, Project
from myapp.serializers import TaskSerializer
from myapp.auth.authentication import AdminTokenAuthtication
from myapp.permission.permission import isDemoAdminUser
from myapp.handler import APIResponse


@api_view(['GET'])
def task_list(request):
    """
    获取所有任务列表
    """
    if request.method == 'GET':
        tasks = Task.objects.filter(is_deleted=False)
        serializer = TaskSerializer(tasks, many=True)
        return APIResponse(code=0, msg='查询成功', data=serializer.data)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def create_task(request):
    """
    创建新任务
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(code=0, msg='创建成功', data=serializer.data)
        return APIResponse(code=1, msg='创建失败', data=serializer.errors)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def update_task(request):
    """
    更新任务信息
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    try:
        task_id = request.GET.get('id')
        task = Task.objects.get(task_id=task_id)
    except Task.DoesNotExist:
        return APIResponse(code=1, msg='任务不存在')

    serializer = TaskSerializer(task, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='更新成功', data=serializer.data)
    return APIResponse(code=1, msg='更新失败', data=serializer.errors)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def delete_task(request):
    """
    删除任务（软删除）
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    try:
        task_ids = request.GET.get('ids').split(',')
        Task.objects.filter(task_id__in=task_ids).update(is_deleted=True)
        return APIResponse(code=0, msg='删除成功')
    except Exception as e:
        return APIResponse(code=1, msg='删除失败', data=str(e))


@api_view(['GET'])
def tasks_by_project(request):
    """
    根据项目ID获取任务列表
    """
    if request.method == 'GET':
        project_id = request.GET.get('project_id')
        if not project_id:
            return APIResponse(code=1, msg='项目ID不能为空')
            
        try:
            project = Project.objects.get(project_id=project_id)
            tasks = Task.objects.filter(project=project, is_deleted=False)
            serializer = TaskSerializer(tasks, many=True)
            return APIResponse(code=0, msg='查询成功', data=serializer.data)
        except Project.DoesNotExist:
            return APIResponse(code=1, msg='项目不存在')