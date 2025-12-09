from rest_framework.decorators import api_view, authentication_classes
from myapp.models import ProjectType
from myapp.serializers import ProjectTypeSerializer
from myapp.auth.authentication import AdminTokenAuthtication
from myapp.permission.permission import isDemoAdminUser
from myapp.handler import APIResponse


@api_view(['GET'])
def project_type_list(request):
    """
    获取所有项目类型列表
    """
    if request.method == 'GET':
        project_types = ProjectType.objects.all()
        serializer = ProjectTypeSerializer(project_types, many=True)
        return APIResponse(code=0, msg='查询成功', data=serializer.data)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def create_project_type(request):
    """
    创建新项目类型
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    if request.method == 'POST':
        serializer = ProjectTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(code=0, msg='创建成功', data=serializer.data)
        return APIResponse(code=1, msg='创建失败', data=serializer.errors)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def update_project_type(request):
    """
    更新项目类型信息
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    try:
        type_id = request.GET.get('id')
        project_type = ProjectType.objects.get(type_id=type_id)
    except ProjectType.DoesNotExist:
        return APIResponse(code=1, msg='项目类型不存在')

    serializer = ProjectTypeSerializer(project_type, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='更新成功', data=serializer.data)
    return APIResponse(code=1, msg='更新失败', data=serializer.errors)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def delete_project_type(request):
    """
    删除项目类型
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    try:
        type_ids = request.GET.get('ids').split(',')
        ProjectType.objects.filter(type_id__in=type_ids).delete()
        return APIResponse(code=0, msg='删除成功')
    except Exception as e:
        return APIResponse(code=1, msg='删除失败', data=str(e))