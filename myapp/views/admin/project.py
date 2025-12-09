from rest_framework.decorators import api_view, authentication_classes
from myapp.models import Project, Department, ProjectType, ProjectStatus
from myapp.serializers import ProjectSerializer
from myapp.auth.authentication import AdminTokenAuthtication
from myapp.permission.permission import isDemoAdminUser
from myapp.handler import APIResponse


@api_view(['GET'])
def project_list(request):
    """
    获取所有项目列表
    """
    if request.method == 'GET':
        projects = Project.objects.filter(is_deleted=False)
        serializer = ProjectSerializer(projects, many=True)
        return APIResponse(code=0, msg='查询成功', data=serializer.data)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def create_project(request):
    """
    创建新项目
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    if request.method == 'POST':
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(code=0, msg='创建成功', data=serializer.data)
        return APIResponse(code=1, msg='创建失败', data=serializer.errors)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def update_project(request):
    """
    更新项目信息
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    try:
        project_id = request.GET.get('id')
        project = Project.objects.get(project_id=project_id)
    except Project.DoesNotExist:
        return APIResponse(code=1, msg='项目不存在')

    serializer = ProjectSerializer(project, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='更新成功', data=serializer.data)
    return APIResponse(code=1, msg='更新失败', data=serializer.errors)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def delete_project(request):
    """
    删除项目（软删除）
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    try:
        project_ids = request.GET.get('ids').split(',')
        Project.objects.filter(project_id__in=project_ids).update(is_deleted=True)
        return APIResponse(code=0, msg='删除成功')
    except Exception as e:
        return APIResponse(code=1, msg='删除失败', data=str(e))