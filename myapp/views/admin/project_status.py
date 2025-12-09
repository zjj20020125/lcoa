from rest_framework.decorators import api_view, authentication_classes
from myapp.models import ProjectStatus
from myapp.serializers import ProjectStatusSerializer
from myapp.auth.authentication import AdminTokenAuthtication
from myapp.permission.permission import isDemoAdminUser
from myapp.handler import APIResponse


@api_view(['GET'])
def project_status_list(request):
    """
    获取所有项目状态列表
    """
    if request.method == 'GET':
        project_statuses = ProjectStatus.objects.all()
        serializer = ProjectStatusSerializer(project_statuses, many=True)
        return APIResponse(code=0, msg='查询成功', data=serializer.data)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def create_project_status(request):
    """
    创建新项目状态
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    if request.method == 'POST':
        serializer = ProjectStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(code=0, msg='创建成功', data=serializer.data)
        return APIResponse(code=1, msg='创建失败', data=serializer.errors)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def update_project_status(request):
    """
    更新项目状态信息
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    try:
        status_id = request.GET.get('id')
        project_status = ProjectStatus.objects.get(status_id=status_id)
    except ProjectStatus.DoesNotExist:
        return APIResponse(code=1, msg='项目状态不存在')

    serializer = ProjectStatusSerializer(project_status, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='更新成功', data=serializer.data)
    return APIResponse(code=1, msg='更新失败', data=serializer.errors)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def delete_project_status(request):
    """
    删除项目状态
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    try:
        status_ids = request.GET.get('ids').split(',')
        ProjectStatus.objects.filter(status_id__in=status_ids).delete()
        return APIResponse(code=0, msg='删除成功')
    except Exception as e:
        return APIResponse(code=1, msg='删除失败', data=str(e))