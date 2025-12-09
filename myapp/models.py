from django.db import models


class User(models.Model):
    GENDER_CHOICES = (
        ('M', '男'),
        ('F', '女'),
    )
    ROLE_CHOICES = (
        ('0', '管理员'),
        ('1', '普通用户'),
    )
    STATUS_CHOICES = (
        ('0', '正常'),
        ('1', '封号'),
    )
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=50, null=True)
    role = models.CharField(max_length=2, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
    nickname = models.CharField(blank=True, null=True, max_length=20)
    avatar = models.FileField(upload_to='avatar/', null=True)
    mobile = models.CharField(max_length=13, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    description = models.TextField(max_length=200, null=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    score = models.IntegerField(default=0, blank=True, null=True)
    push_email = models.CharField(max_length=40, blank=True, null=True)
    push_switch = models.BooleanField(blank=True, null=True, default=False)
    admin_token = models.CharField(max_length=32, blank=True, null=True)
    token = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = "b_user"


class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "b_tag"


class Classification(models.Model):
    list_display = ("title", "id")
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "b_classification"


class Thing(models.Model):
    STATUS_CHOICES = (
        ('0', '上架'),
        ('1', '下架'),
    )
    id = models.BigAutoField(primary_key=True)
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE, blank=True, null=True,
                                       related_name='classification_thing')
    tag = models.ManyToManyField(Tag, blank=True)
    title = models.CharField(max_length=30, blank=True, null=True)
    property = models.CharField(max_length=30, blank=True, null=True)
    price = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=30, blank=True, null=True)
    cover = models.ImageField(upload_to='cover/', null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
    create_time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "b_thing"


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = models.CharField(max_length=200, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='user_comment')
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE, null=True, related_name='thing_comment')
    comment_time = models.DateTimeField(auto_now_add=True, null=True)
    like_count = models.IntegerField(default=0)

    class Meta:
        db_table = "b_comment"


class Record(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='user_record')
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE, null=True, related_name='thing_record')
    title = models.CharField(max_length=100, blank=True, null=True)
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE, null=True,
                                       related_name='classification')
    record_time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "b_record"


class LoginLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=50, blank=True, null=True)
    ip = models.CharField(max_length=100, blank=True, null=True)
    ua = models.CharField(max_length=200, blank=True, null=True)
    log_time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "b_login_log"


class OpLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    re_ip = models.CharField(max_length=100, blank=True, null=True)
    re_time = models.DateTimeField(auto_now_add=True, null=True)
    re_url = models.CharField(max_length=200, blank=True, null=True)
    re_method = models.CharField(max_length=10, blank=True, null=True)
    re_content = models.CharField(max_length=200, blank=True, null=True)
    access_time = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = "b_op_log"


class ErrorLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    ip = models.CharField(max_length=100, blank=True, null=True)
    url = models.CharField(max_length=200, blank=True, null=True)
    method = models.CharField(max_length=10, blank=True, null=True)
    content = models.CharField(max_length=200, blank=True, null=True)
    log_time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "b_error_log"


class Banner(models.Model):
    id = models.BigAutoField(primary_key=True)
    image = models.ImageField(upload_to='banner/', null=True)
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE, null=True, related_name='thing_banner')
    create_time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "b_banner"


class Ad(models.Model):
    id = models.BigAutoField(primary_key=True)
    image = models.ImageField(upload_to='ad/', null=True)
    link = models.CharField(max_length=500, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "b_ad"


class Notice(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    content = models.CharField(max_length=1000, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "b_notice"


class Address(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='user_address')
    name = models.CharField(max_length=100, blank=True, null=True)
    mobile = models.CharField(max_length=30, blank=True, null=True)
    desc = models.CharField(max_length=300, blank=True, null=True)
    default = models.BooleanField(blank=True, null=True, default=False)  # 是否默认地址
    create_time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "b_address"


class Lcoa(models.Model):
    # 根据第一个表中读取的列名称定义字段
    extracted_date = models.CharField(max_length=20, null=True)  # 从文件名提取的日期
    process_node_id = models.CharField(max_length=100, null=True)  # 流程节点id
    process_id = models.CharField(max_length=100, null=True)  # 流程id
    process_title = models.CharField(max_length=200, null=True)  # 流程标题
    process_name = models.CharField(max_length=200, null=True)  # 流程名称
    process_type = models.CharField(max_length=100, null=True)  # 流程类型
    branch = models.CharField(max_length=100, null=True)  # 所属分部
    department = models.CharField(max_length=100, null=True)  # 所属部门
    node_operator = models.CharField(max_length=100, null=True)  # 节点操作者
    node_operation_type = models.CharField(max_length=100, null=True)  # 节点操作类型
    node_name = models.CharField(max_length=100, null=True)  # 节点名称
    first_receive_time = models.CharField(max_length=50, null=True)  # 最初接收时间
    last_process_time = models.CharField(max_length=50, null=True)  # 最后处理时间
    total_duration = models.CharField(max_length=50, null=True)  # 总计耗时
    total_timeout = models.CharField(max_length=50, null=True)  # 总计超时

    class Meta:
        db_table = "lcoa"


# 新增项目管理系统的模型
class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "departments"


class ProjectType(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "project_types"


class ProjectStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = "project_statuses"


# 为项目管理系统新增的用户模型
class ProjectUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=50)
    position = models.CharField(max_length=50, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.RESTRICT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "users"


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=100)
    project_no = models.CharField(max_length=50, unique=True)
    type = models.ForeignKey(ProjectType, on_delete=models.RESTRICT)
    progress = models.SmallIntegerField(default=0)
    department = models.ForeignKey(Department, on_delete=models.RESTRICT)
    status = models.ForeignKey(ProjectStatus, on_delete=models.RESTRICT)
    plan_start_time = models.DateField()
    plan_end_time = models.DateField()
    manager = models.ForeignKey('self', on_delete=models.RESTRICT, null=True, blank=True)  # 项目经理
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "projects"


class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=100)
    duration = models.IntegerField(null=True, blank=True)
    plan_start_time = models.DateField(null=True, blank=True)
    plan_end_time = models.DateField(null=True, blank=True)
    actual_start_time = models.DateField(null=True, blank=True)
    actual_end_time = models.DateField(null=True, blank=True)
    predecessor_task = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    assignee = models.ForeignKey(ProjectUser, on_delete=models.SET_NULL, null=True, blank=True)
    progress = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "tasks"