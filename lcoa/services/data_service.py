"""
数据服务模块
提供各种数据保存和处理功能
"""
from sqlalchemy import func

def save_to_lcoa_table(db, Lcoa, data):
    """
    保存数据到lcoa表，使用更高效的批量处理方式
    
    Args:
        db: SQLAlchemy数据库实例
        Lcoa: Lcoa模型类
        data (list): 要保存的数据列表
    """
    try:
        # 先获取所有现有的记录，构建一个字典用于快速查找
        existing_records = {}
        for record in Lcoa.query.all():
            key = (record.process_id, record.process_node_id)
            existing_records[key] = record

        print(f"数据库中已存在 {len(existing_records)} 条记录")

        records_to_add = []
        updated_count = 0

        for row in data:
            # 提取用于判断是否为同一条记录的字段
            extracted_date = row[0] if len(row) > 0 else ''
            process_id = row[1] if len(row) > 1 else ''
            process_node_id = row[2] if len(row) > 2 else ''  # 修正索引，根据实际数据结构

            # 构造查找键
            key = (process_id, process_node_id)

            if key in existing_records:
                # 更新现有记录
                existing_record = existing_records[key]
                existing_record.extracted_date = extracted_date
                existing_record.process_title = row[3] if len(row) > 3 else ''
                existing_record.process_name = row[4] if len(row) > 4 else ''
                existing_record.process_type = row[5] if len(row) > 5 else ''
                existing_record.branch = row[6] if len(row) > 6 else ''
                existing_record.department = row[7] if len(row) > 7 else ''
                existing_record.node_operator = row[8] if len(row) > 8 else ''
                existing_record.node_operation_type = row[9] if len(row) > 9 else ''
                existing_record.node_name = row[10] if len(row) > 10 else ''
                existing_record.first_receive_time = row[11] if len(row) > 11 else ''
                existing_record.last_process_time = row[12] if len(row) > 12 else ''
                existing_record.total_duration = row[13] if len(row) > 13 else ''
                existing_record.total_timeout = row[14] if len(row) > 14 else ''
                updated_count += 1
            else:
                # 创建新记录
                record = Lcoa(
                    extracted_date=extracted_date,
                    process_node_id=process_node_id,
                    process_id=process_id,
                    process_title=row[3] if len(row) > 3 else '',
                    process_name=row[4] if len(row) > 4 else '',
                    process_type=row[5] if len(row) > 5 else '',
                    branch=row[6] if len(row) > 6 else '',
                    department=row[7] if len(row) > 7 else '',
                    node_operator=row[8] if len(row) > 8 else '',
                    node_operation_type=row[9] if len(row) > 9 else '',
                    node_name=row[10] if len(row) > 10 else '',
                    first_receive_time=row[11] if len(row) > 11 else '',
                    last_process_time=row[12] if len(row) > 12 else '',
                    total_duration=row[13] if len(row) > 13 else '',
                    total_timeout=row[14] if len(row) > 14 else ''
                )
                records_to_add.append(record)

        # 批量添加新记录
        if records_to_add:
            db.session.bulk_save_objects(records_to_add)

        # 提交事务
        db.session.commit()
        print(f"成功保存到lcoa表: 新增 {len(records_to_add)} 条记录, 更新 {updated_count} 条记录")

    except Exception as e:  # 将异常处理移到 with 块内部
        db.session.rollback()
        print(f"保存数据到lcoa表时出错: {e}")
        import traceback
        traceback.print_exc()


def save_to_sys_nodeal_table_with_comparison(db, SysNodeal, data):
    """
    保存数据到sys_nodeal表，如果第二列和第三列数据相同则更新现有记录
    """
    try:
        # 获取所有现有记录，建立索引以便快速查找
        existing_records = {}
        for record in SysNodeal.query.all():
            key = (record.process_node_id, record.process_id)
            existing_records[key] = record

        records_to_add = []
        updated_count = 0

        for row in data:
            # 构造查找键（第二列和第三列）
            key = (row[1] if len(row) > 1 else '', row[2] if len(row) > 2 else '')

            if key in existing_records:
                # 更新现有记录
                existing_record = existing_records[key]
                existing_record.extracted_date = row[0] if len(row) > 0 else ''
                existing_record.process_title = row[3] if len(row) > 3 else ''
                existing_record.process_name = row[4] if len(row) > 4 else ''
                existing_record.process_type = row[5] if len(row) > 5 else ''
                existing_record.branch = row[6] if len(row) > 6 else ''
                existing_record.department = row[7] if len(row) > 7 else ''
                existing_record.node_operator = row[8] if len(row) > 8 else ''
                existing_record.node_operation_type = row[9] if len(row) > 9 else ''
                existing_record.node_name = row[10] if len(row) > 10 else ''
                existing_record.first_receive_time = row[11] if len(row) > 11 else ''
                existing_record.last_process_time = row[12] if len(row) > 12 else ''
                existing_record.total_duration = row[13] if len(row) > 13 else ''
                existing_record.total_timeout = row[14] if len(row) > 14 else ''
                updated_count += 1
            else:
                # 创建新记录
                record = SysNodeal(
                    extracted_date=row[0] if len(row) > 0 else '',
                    process_node_id=row[1] if len(row) > 1 else '',
                    process_id=row[2] if len(row) > 2 else '',
                    process_title=row[3] if len(row) > 3 else '',
                    process_name=row[4] if len(row) > 4 else '',
                    process_type=row[5] if len(row) > 5 else '',
                    branch=row[6] if len(row) > 6 else '',
                    department=row[7] if len(row) > 7 else '',
                    node_operator=row[8] if len(row) > 8 else '',
                    node_operation_type=row[9] if len(row) > 9 else '',
                    node_name=row[10] if len(row) > 10 else '',
                    first_receive_time=row[11] if len(row) > 11 else '',
                    last_process_time=row[12] if len(row) > 12 else '',
                    total_duration=row[13] if len(row) > 13 else '',
                    total_timeout=row[14] if len(row) > 14 else ''
                )
                records_to_add.append(record)

        # 批量添加新记录
        if records_to_add:
            db.session.bulk_save_objects(records_to_add)

        # 提交事务
        db.session.commit()
        print(f"成功保存到sys_nodeal表: 新增 {len(records_to_add)} 条记录, 更新 {updated_count} 条记录")

    except Exception as e:  # 异常处理在 with 块内部
        db.session.rollback()
        print(f"保存数据到sys_nodeal表时出错: {e}")
        import traceback
        traceback.print_exc()


def save_to_sys_xiangxi_table(db, SysXiangxi, data):
    """
    保存数据到sys_xiangxi表，使用批量插入提高性能
    
    Args:
        db: SQLAlchemy数据库实例
        SysXiangxi: SysXiangxi模型类
        data (list): 要保存的数据列表
    """
    try:
        records_to_add = []
        for row in data:
            # 创建SysXiangxi对象
            record = SysXiangxi(
                extracted_date=row[0] if len(row) > 0 else '',
                node_operator=row[1] if len(row) > 1 else '',
                department=row[2] if len(row) > 2 else '',
                node_operation_type=row[3] if len(row) > 3 else '',
                quantity=row[4] if len(row) > 4 else ''
            )
            records_to_add.append(record)
        
        # 批量添加记录
        if records_to_add:
            db.session.bulk_save_objects(records_to_add)
        
        # 提交事务
        db.session.commit()
        print(f"成功保存 {len(records_to_add)} 条记录到sys_xiangxi表")
    except Exception as e:
        db.session.rollback()
        print(f"保存数据到sys_xiangxi表时出错: {e}")


def save_to_sys_club_table(db, SysClub, data):
    """
    保存数据到sys_club表，使用批量插入提高性能
    
    Args:
        db: SQLAlchemy数据库实例
        SysClub: SysClub模型类
        data (list): 要保存的数据列表
    """
    try:
        records_to_add = []
        for row in data:
            # 创建SysClub对象
            record = SysClub(
                extracted_date=row[0] if len(row) > 0 else '',
                department=row[1] if len(row) > 1 else '',
                personnel_count=row[2] if len(row) > 2 else '',
                timeout_count=row[3] if len(row) > 3 else ''
            )
            records_to_add.append(record)
        
        # 批量添加记录
        if records_to_add:
            db.session.bulk_save_objects(records_to_add)
        
        # 提交事务
        db.session.commit()
        print(f"成功保存 {len(records_to_add)} 条记录到sys_club表")
    except Exception as e:
        db.session.rollback()
        print(f"保存数据到sys_club表时出错: {e}")


def save_to_sys_club_table_with_comparison(db, SysClub, data):
    """
    保存数据到sys_club表，如果前两个数据相同则更新现有记录
    
    Args:
        db: SQLAlchemy数据库实例
        SysClub: SysClub模型类
        data (list): 要保存的数据列表
    """
    try:
        # 获取所有现有记录，建立索引以便快速查找
        existing_records = {}
        for record in SysClub.query.all():
            key = (record.department, record.personnel_count)  # 前两列对应department和personnel_count
            existing_records[key] = record
        
        records_to_add = []
        updated_count = 0
        
        for row in data:
            # 构造查找键（前两列）
            key = (row[1] if len(row) > 1 else '', row[2] if len(row) > 2 else '')  # 第一列是日期
            
            if key in existing_records:
                # 更新现有记录
                existing_record = existing_records[key]
                existing_record.extracted_date = row[0] if len(row) > 0 else ''
                existing_record.timeout_count = row[3] if len(row) > 3 else ''
                updated_count += 1
            else:
                # 创建新记录
                record = SysClub(
                    extracted_date=row[0] if len(row) > 0 else '',
                    department=row[1] if len(row) > 1 else '',
                    personnel_count=row[2] if len(row) > 2 else '',
                    timeout_count=row[3] if len(row) > 3 else ''
                )
                records_to_add.append(record)
        
        # 批量添加新记录
        if records_to_add:
            db.session.bulk_save_objects(records_to_add)
        
        # 提交事务
        db.session.commit()
        print(f"成功保存到sys_club表: 新增 {len(records_to_add)} 条记录, 更新 {updated_count} 条记录")
    except Exception as e:
        db.session.rollback()
        print(f"保存数据到sys_club表时出错: {e}")
        import traceback
        traceback.print_exc()


def save_to_sys_nodeal_table_with_comparison(db, SysNodeal, data):
    """
    保存数据到sys_nodeal表，如果第二列和第三列数据相同则更新现有记录
    
    Args:
        db: SQLAlchemy数据库实例
        SysNodeal: SysNodeal模型类
        data (list): 要保存的数据列表
    """
    try:
        # 获取所有现有记录，建立索引以便快速查找
        existing_records = {}
        for record in SysNodeal.query.all():
            key = (record.process_node_id, record.process_id)  # 第二列和第三列对应process_node_id和process_id
            existing_records[key] = record
        
        records_to_add = []
        updated_count = 0
        
        for row in data:
            # 构造查找键（第二列和第三列）
            key = (row[1] if len(row) > 1 else '', row[2] if len(row) > 2 else '')
            
            if key in existing_records:
                # 更新现有记录
                existing_record = existing_records[key]
                existing_record.extracted_date = row[0] if len(row) > 0 else ''
                existing_record.process_title = row[3] if len(row) > 3 else ''
                existing_record.process_name = row[4] if len(row) > 4 else ''
                existing_record.process_type = row[5] if len(row) > 5 else ''
                existing_record.branch = row[6] if len(row) > 6 else ''
                existing_record.department = row[7] if len(row) > 7 else ''
                existing_record.node_operator = row[8] if len(row) > 8 else ''
                existing_record.node_operation_type = row[9] if len(row) > 9 else ''
                existing_record.node_name = row[10] if len(row) > 10 else ''
                existing_record.first_receive_time = row[11] if len(row) > 11 else ''
                existing_record.last_process_time = row[12] if len(row) > 12 else ''
                existing_record.total_duration = row[13] if len(row) > 13 else ''
                existing_record.total_timeout = row[14] if len(row) > 14 else ''
                updated_count += 1
            else:
                # 创建新记录
                record = SysNodeal(
                    extracted_date=row[0] if len(row) > 0 else '',
                    process_node_id=row[1] if len(row) > 1 else '',
                    process_id=row[2] if len(row) > 2 else '',
                    process_title=row[3] if len(row) > 3 else '',
                    process_name=row[4] if len(row) > 4 else '',
                    process_type=row[5] if len(row) > 5 else '',
                    branch=row[6] if len(row) > 6 else '',
                    department=row[7] if len(row) > 7 else '',
                    node_operator=row[8] if len(row) > 8 else '',
                    node_operation_type=row[9] if len(row) > 9 else '',
                    node_name=row[10] if len(row) > 10 else '',
                    first_receive_time=row[11] if len(row) > 11 else '',
                    last_process_time=row[12] if len(row) > 12 else '',
                    total_duration=row[13] if len(row) > 13 else '',
                    total_timeout=row[14] if len(row) > 14 else ''
                )
                records_to_add.append(record)
        
        # 批量添加新记录
        if records_to_add:
            db.session.bulk_save_objects(records_to_add)
        
        # 提交事务
        db.session.commit()
        print(f"成功保存到sys_nodeal表: 新增 {len(records_to_add)} 条记录, 更新 {updated_count} 条记录")
    except Exception as e:
        db.session.rollback()
        print(f"保存数据到sys_nodeal表时出错: {e}")
        import traceback
        traceback.print_exc()


def save_to_sys_xiangxi_table_with_comparison(db, SysXiangxi, data):
    """
    保存数据到sys_xiangxi表，如果前两个数据相同则更新现有记录
    
    Args:
        db: SQLAlchemy数据库实例
        SysXiangxi: SysXiangxi模型类
        data (list): 要保存的数据列表
    """
    try:
        # 获取所有现有记录，建立索引以便快速查找
        existing_records = {}
        for record in SysXiangxi.query.all():
            key = (record.node_operator, record.department)  # 前两列对应node_operator和department
            existing_records[key] = record
        
        records_to_add = []
        updated_count = 0
        
        for row in data:
            # 构造查找键（前两列）
            key = (row[1] if len(row) > 1 else '', row[2] if len(row) > 2 else '')  # 第一列是日期
            
            if key in existing_records:
                # 更新现有记录
                existing_record = existing_records[key]
                existing_record.extracted_date = row[0] if len(row) > 0 else ''
                existing_record.node_operation_type = row[3] if len(row) > 3 else ''
                existing_record.quantity = row[4] if len(row) > 4 else ''
                updated_count += 1
            else:
                # 创建新记录
                record = SysXiangxi(
                    extracted_date=row[0] if len(row) > 0 else '',
                    node_operator=row[1] if len(row) > 1 else '',
                    department=row[2] if len(row) > 2 else '',
                    node_operation_type=row[3] if len(row) > 3 else '',
                    quantity=row[4] if len(row) > 4 else ''
                )
                records_to_add.append(record)
        
        # 批量添加新记录
        if records_to_add:
            db.session.bulk_save_objects(records_to_add)
        
        # 提交事务
        db.session.commit()
        print(f"成功保存到sys_xiangxi表: 新增 {len(records_to_add)} 条记录, 更新 {updated_count} 条记录")
    except Exception as e:
        db.session.rollback()
        print(f"保存数据到sys_xiangxi表时出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pass