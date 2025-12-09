from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from myapp.models import Department
from myapp.serializers import DepartmentSerializer
from myapp.auth.authentication import AdminTokenAuthtication
from myapp.permission.permission import isDemoAdminUser
from myapp.handler import APIResponse


@api_view(['GET'])
def department_list(request):
    """
    获取所有部门列表
    """
    if request.method == 'GET':
        departments = Department.objects.filter(is_deleted=False)
        serializer = DepartmentSerializer(departments, many=True)
        return APIResponse(code=0, msg='查询成功', data=serializer.data)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def create_department(request):
    """
    创建新部门
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    if request.method == 'POST':
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse(code=0, msg='创建成功', data=serializer.data)
        return APIResponse(code=1, msg='创建失败', data=serializer.errors)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def update_department(request):
    """
    更新部门信息
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    try:
        department_id = request.GET.get('id')
        department = Department.objects.get(department_id=department_id)
    except Department.DoesNotExist:
        return APIResponse(code=1, msg='部门不存在')

    serializer = DepartmentSerializer(department, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='更新成功', data=serializer.data)
    return APIResponse(code=1, msg='更新失败', data=serializer.errors)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def delete_department(request):
    """
    删除部门（软删除）
    """
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='演示帐号无法操作')
        
    try:
        department_ids = request.GET.get('ids').split(',')
        Department.objects.filter(department_id__in=department_ids).update(is_deleted=True)
        return APIResponse(code=0, msg='删除成功')
    except Exception as e:
        return APIResponse(code=1, msg='删除失败', data=str(e))