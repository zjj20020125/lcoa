import pandas as pd
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 延迟导入，确保路径设置完成后再导入
try:
    from lcoa.app import db, SysProject, SysProjectMilestone
except ImportError:
    # 如果上面的方式失败，尝试直接导入
    try:
        from app import db, SysProject, SysProjectMilestone
    except ImportError:
        # 最后尝试使用相对导入
        from ..app import db, SysProject, SysProjectMilestone

from datetime import datetime


def sort_and_validate_milestones(milestones):
    """
    对里程碑按时间顺序进行排序和验证
    
    Args:
        milestones (list): 里程碑列表
        
    Returns:
        tuple: (sorted_milestones, is_valid, errors)
    """
    if not milestones:
        return milestones, True, []
    
    # 按计划开始时间排序
    try:
        # 过滤掉没有计划开始时间的里程碑
        valid_milestones = [m for m in milestones if m.get('planned_start_time')]
        sorted_milestones = sorted(valid_milestones, key=lambda x: parse_date(x.get('planned_start_time', '')))
    except Exception as e:
        return milestones, False, [f"排序里程碑时出错: {str(e)}"]
    
    errors = []
    is_valid = True
    
    # 验证时间逻辑
    for i in range(len(sorted_milestones) - 1):
        current = sorted_milestones[i]
        next_milestone = sorted_milestones[i + 1]
        
        current_end = parse_date(current.get('planned_end_time', ''))
        next_start = parse_date(next_milestone.get('planned_start_time', ''))
        
        # 检查当前里程碑的结束时间是否早于或等于下一个里程碑的开始时间
        if current_end and next_start and current_end > next_start:
            is_valid = False
            errors.append(
                f"里程碑 '{current.get('milestone', '')}' 的计划结束时间 "
                f"({current.get('planned_end_time', '')}) 晚于 "
                f"下一个里程碑 '{next_milestone.get('milestone', '')}' 的计划开始时间 "
                f"({next_milestone.get('planned_start_time', '')})"
            )
    
    # 为里程碑添加序号
    for i, milestone in enumerate(sorted_milestones):
        milestone['milestone'] = f"{i+1}号里程碑节点 - {milestone.get('milestone', '')}"
    
    return sorted_milestones, is_valid, errors


def parse_date(date_str):
    """
    解析日期字符串
    
    Args:
        date_str (str): 日期字符串
        
    Returns:
        datetime: 解析后的日期对象，如果解析失败则返回None
    """
    if not date_str or pd.isna(date_str):
        return None
    
    date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%Y年%m月%d日']
    
    for fmt in date_formats:
        try:
            return datetime.strptime(str(date_str), fmt)
        except ValueError:
            continue
    
    return None


def import_projects_from_excel(file_path):
    """
    从Excel文件导入项目数据到数据库
    
    Excel格式要求:
    - 单个工作表包含所有信息
    - 第一行为表头行，不应作为数据导入
    - 列: 项目名称, 产品名称, 客户名称及订单情况等
    
    Args:
        file_path (str): Excel文件路径
        
    Returns:
        dict: 导入结果
    """
    try:
        # 读取第一个工作表
        df = pd.read_excel(file_path, sheet_name=0)
        
        # 检查必要的列是否存在
        # 映射列名
        column_mapping = {
            '项目名称': ['项目名称', 'Unnamed: 1'],
            '产品名称': ['产品名称', 'Unnamed: 2'],
            '客户名称及订单情况': ['客户名称及订单情况', 'Unnamed: 4']
        }
        
        # 检查并映射列名
        mapped_columns = {}
        for required_col, possible_names in column_mapping.items():
            found = False
            for name in possible_names:
                if name in df.columns:
                    mapped_columns[required_col] = name
                    found = True
                    break
            if not found:
                return {
                    'success': False,
                    'message': f'缺少必要列: {required_col}'
                }
        
        # 重命名列以匹配期望的名称
        rename_mapping = {v: k for k, v in mapped_columns.items()}
        df = df.rename(columns=rename_mapping)
        
        # 跳过表头行（第一行），只处理真正的数据行
        # 通过检查项目名称是否为表头标识来判断
        data_rows = df[
            (df['项目名称'].notna()) & 
            (df['项目名称'] != '项目名称') & 
            (df['项目名称'] != 'Unnamed: 1') &
            (df['项目名称'].astype(str).str.strip() != '')
        ]
        
        imported_projects = []
        failed_projects = []
        
        # 遍历数据行
        for index, row in data_rows.iterrows():
            try:
                # 处理客户名称和订单情况
                customer_name = ''
                order_status = ''
                if '客户名称及订单情况' in row and pd.notna(row['客户名称及订单情况']):
                    customer_info = str(row['客户名称及订单情况'])
                    # 尝试分离客户名称和订单情况
                    if '(' in customer_info and customer_info.endswith(')'):
                        parts = customer_info.rsplit('(', 1)
                        customer_name = parts[0]
                        order_status = parts[1][:-1]  # 移除最后的')'
                    else:
                        customer_name = customer_info
                
                # 创建项目记录
                project = SysProject(
                    project_name=str(row['项目名称']) if pd.notna(row['项目名称']) else '',
                    product_name=str(row['产品名称']) if pd.notna(row['产品名称']) else '',
                    customer_name=customer_name,
                    order_status=order_status
                )
                
                db.session.add(project)
                db.session.flush()  # 获取项目ID但不提交事务
                
                project_info = {
                    'id': project.id,
                    'project_name': project.project_name,
                    'product_name': project.product_name,
                    'customer_name': project.customer_name,
                    'order_status': project.order_status
                }
                
                imported_projects.append(project_info)
                
                # 打印即将存储的项目数据
                print(f"准备存储项目 - ID: {project.id}, 名称: {project.project_name}, 产品: {project.product_name}, 客户: {project.customer_name}")
                
            except Exception as e:
                failed_projects.append({
                    'row': index + 1,
                    'data': row.to_dict(),
                    'error': str(e)
                })
        
        # 提交项目事务
        print(f"正在提交 {len(imported_projects)} 个项目和 {len(failed_projects)} 个失败项目到数据库...")
        db.session.commit()
        print(f"项目数据已成功提交到数据库")
        
        result = {
            'success': True,
            'message': f'成功导入 {len(imported_projects)} 个项目',
            'imported_projects': imported_projects,
            'failed_projects': failed_projects
        }
        
        # 从同一工作表中提取里程碑数据
        try:
            result['milestone_import'] = import_milestones_from_single_sheet(file_path, imported_projects)
        except Exception as e:
            result['milestone_import_warning'] = f'导入里程碑数据时出错: {str(e)}'
        
        return result
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'导入失败: {str(e)}'
        }

def import_milestones_from_single_sheet(file_path, imported_projects):
    """
    从单个工作表中导入里程碑数据
    
    Args:
        file_path (str): Excel文件路径
        imported_projects (list): 已导入的项目列表
        
    Returns:
        dict: 里程碑导入结果
    """
    try:
        # 读取第一个工作表
        df = pd.read_excel(file_path, sheet_name=0)
        
        # 映射列名
        milestone_column_mapping = {
            '项目名称': ['项目名称', 'Unnamed: 1'],
            '关键节点': ['关键里程碑节点', 'Unnamed: 5'],
            '负责部门': ['责任部门', 'Unnamed: 6'],
            '计划开始时间': ['计划开始时间', 'Unnamed: 7'],
            '计划结束时间': ['计划结束时间', 'Unnamed: 8'],
            '实际完成时间': ['实际完成时间', 'Unnamed: 9'],
            '负责人': ['负责人', 'Unnamed: 10'],
            '异常类别': ['异常类别', 'Unnamed: 11'],
            '影响周期': ['影响周期（天）', 'Unnamed: 12'],
            '应对措施': ['应对措施', 'Unnamed: 13']
        }
        
        # 检查并映射列名
        mapped_milestone_columns = {}
        for required_col, possible_names in milestone_column_mapping.items():
            found = False
            for name in possible_names:
                if name in df.columns:
                    mapped_milestone_columns[required_col] = name
                    found = True
                    break
            # 注意：这里不要求所有列都存在，因为有些是可选的
            
        # 重命名列以匹配期望的名称
        milestone_rename_mapping = {v: k for k, v in mapped_milestone_columns.items()}
        df = df.rename(columns=milestone_rename_mapping)
        
        imported_milestones = []
        failed_milestones = []
        
        # 创建项目名称到ID的映射
        project_name_to_id = {proj['project_name']: proj['id'] for proj in imported_projects}
        
        # 按项目分组收集里程碑
        project_milestones = {}
        
        # 跟踪当前项目
        current_project_name = ""
        current_project_id = None
        
        # 遍历每一行数据
        for index, row in df.iterrows():
            try:
                # 检查项目名称
                project_name_cell = row.get('项目名称', '')
                
                # 如果有项目名称，则更新当前项目
                if pd.notna(project_name_cell) and str(project_name_cell).strip() != '':
                    current_project_name = str(project_name_cell).strip()
                    # 查找项目ID
                    current_project_id = project_name_to_id.get(current_project_name)
                    if current_project_id is None:
                        # 尝试模糊匹配项目名称
                        for pname, pid in project_name_to_id.items():
                            if current_project_name.startswith(pname) or pname.startswith(current_project_name):
                                current_project_id = pid
                                current_project_name = pname  # 使用匹配到的项目名称
                                break
                
                # 检查关键节点是否为空
                milestone_cell = row.get('关键节点', '')
                if pd.isna(milestone_cell) or str(milestone_cell).strip() == '':
                    continue  # 跳过空的关键节点
                
                # 如果没有找到对应的项目ID，则记录错误
                if current_project_id is None:
                    failed_milestones.append({
                        'row': index + 1,
                        'reason': f'找不到对应的项目: {current_project_name}'
                    })
                    continue
                
                # 初始化项目里程碑列表
                if current_project_id not in project_milestones:
                    project_milestones[current_project_id] = []
                
                # 收集里程碑数据
                milestone_data = {
                    'project_id': current_project_id,
                    'project_name': current_project_name,
                    'milestone': str(milestone_cell) if pd.notna(milestone_cell) else '',
                    'responsible_department': str(row.get('负责部门', '')) if pd.notna(row.get('负责部门', '')) else '',
                    'planned_start_time': str(row.get('计划开始时间', '')) if pd.notna(row.get('计划开始时间', '')) else '',
                    'planned_end_time': str(row.get('计划结束时间', '')) if pd.notna(row.get('计划结束时间', '')) else '',
                    'actual_completion_time': str(row.get('实际完成时间', '')) if pd.notna(row.get('实际完成时间', '')) else '',
                    'responsible_person': str(row.get('负责人', '')) if pd.notna(row.get('负责人', '')) else '',
                    'exception_type': str(row.get('异常类别', '')) if pd.notna(row.get('异常类别', '')) else '',
                    'impact_cycle': str(row.get('影响周期', '')) if pd.notna(row.get('影响周期', '')) else '',
                    'response_measures': str(row.get('应对措施', '')) if pd.notna(row.get('应对措施', '')) else ''
                }
                
                project_milestones[current_project_id].append(milestone_data)
                
            except Exception as e:
                failed_milestones.append({
                    'row': index + 1,
                    'data': row.to_dict(),
                    'error': str(e)
                })
        
        # 对每个项目的里程碑进行排序和验证
        for project_id, milestones in project_milestones.items():
            if not milestones:
                continue
                
            # 排序并验证里程碑
            sorted_milestones, is_valid, errors = sort_and_validate_milestones(milestones)
            
            # 如果验证失败，记录错误
            if not is_valid:
                for error in errors:
                    failed_milestones.append({
                        'project_id': project_id,
                        'reason': error
                    })
            
            # 为有效的里程碑创建数据库记录
            for milestone_data in sorted_milestones:
                try:
                    # 创建里程碑记录
                    milestone = SysProjectMilestone(
                        project_id=milestone_data['project_id'],
                        milestone=milestone_data['milestone'],  # 已经包含了序号
                        responsible_department=milestone_data['responsible_department'],
                        planned_start_time=milestone_data['planned_start_time'],
                        planned_end_time=milestone_data['planned_end_time'],
                        actual_completion_time=milestone_data['actual_completion_time'],
                        responsible_person=milestone_data['responsible_person'],
                        exception_type=milestone_data['exception_type'],
                        impact_cycle=milestone_data['impact_cycle'],
                        response_measures=milestone_data['response_measures']
                    )
                    
                    db.session.add(milestone)
                    imported_milestones.append(milestone_data)
                    
                    # 打印即将存储的里程碑数据
                    print(f"准备存储里程碑 - 项目ID: {milestone_data['project_id']}, 项目名称: {milestone_data['project_name']}, 里程碑: {milestone_data['milestone']}")
                    
                except Exception as e:
                    failed_milestones.append({
                        'project_data': milestone_data,
                        'error': str(e)
                    })
        
        # 提交事务
        print(f"正在提交数据到数据库...")
        db.session.commit()
        print(f"数据已成功提交到数据库")
        
        return {
            'success': True,
            'message': f'成功导入 {len(imported_milestones)} 个里程碑',
            'imported_milestones': imported_milestones,
            'failed_milestones': failed_milestones
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'导入里程碑失败: {str(e)}'
        }

def import_milestones_from_excel(file_path, imported_projects):
    """
    从Excel文件导入里程碑数据
    
    Args:
        file_path (str): Excel文件路径
        imported_projects (list): 已导入的项目列表
        
    Returns:
        dict: 里程碑导入结果
    """
    try:
        # 读取第二个工作表（里程碑信息）
        milestone_df = pd.read_excel(file_path, sheet_name=1)
        
        # 检查必要的列是否存在
        # 映射列名
        milestone_column_mapping = {
            '项目名称': ['项目名称', 'Unnamed: 1'],
            '关键节点': ['关键里程碑节点', 'Unnamed: 5'],
            '负责部门': ['责任部门', 'Unnamed: 6'],
            '计划开始时间': ['计划开始时间', 'Unnamed: 7'],
            '计划结束时间': ['计划结束时间', 'Unnamed: 8']
        }
        
        # 检查并映射列名
        mapped_milestone_columns = {}
        for required_col, possible_names in milestone_column_mapping.items():
            found = False
            for name in possible_names:
                if name in milestone_df.columns:
                    mapped_milestone_columns[required_col] = name
                    found = True
                    break
            if not found:
                return {
                    'success': False,
                    'message': f'里程碑工作表缺少必要列: {required_col}'
                }
        
        # 重命名列以匹配期望的名称
        milestone_rename_mapping = {v: k for k, v in mapped_milestone_columns.items()}
        milestone_df = milestone_df.rename(columns=milestone_rename_mapping)
        
        imported_milestones = []
        failed_milestones = []
        
        # 创建项目名称到ID的映射
        project_name_to_id = {proj['project_name']: proj['id'] for proj in imported_projects}
        
        # 按项目名称分组，便于处理一个项目对应多个里程碑的情况
        if '项目名称' in milestone_df.columns:
            grouped_milestones = milestone_df.groupby('项目名称')
        else:
            # 如果没有项目名称列，则无法处理里程碑数据
            return {
                'success': False,
                'message': '里程碑工作表缺少项目名称列，无法关联到具体项目'
            }
        
        # 遍历每个项目组
        for project_name, group in grouped_milestones:
            project_name_str = str(project_name) if pd.notna(project_name) else ''
            
            if project_name_str not in project_name_to_id:
                # 记录所有属于该项目的里程碑行的错误
                for index, row in group.iterrows():
                    failed_milestones.append({
                        'row': index + 1,
                        'reason': f'找不到对应的项目: {project_name_str}'
                    })
                continue
            
            project_id = project_name_to_id[project_name_str]
            
            # 为该项目的所有里程碑创建记录
            for index, row in group.iterrows():
                try:
                    # 检查关键节点是否为空
                    if pd.isna(row['关键节点']) or str(row['关键节点']).strip() == '':
                        continue  # 跳过空的关键节点
                    
                    # 创建里程碑记录
                    milestone = SysProjectMilestone(
                        project_id=project_id,
                        milestone=str(row['关键节点']) if pd.notna(row['关键节点']) else '',
                        responsible_department=str(row.get('负责部门', '')) if pd.notna(row.get('负责部门', '')) else '',
                        planned_start_time=str(row.get('计划开始时间', '')) if pd.notna(row.get('计划开始时间', '')) else '',
                        planned_end_time=str(row.get('计划结束时间', '')) if pd.notna(row.get('计划结束时间', '')) else '',
                        actual_completion_time=str(row.get('实际完成时间', '')) if pd.notna(row.get('实际完成时间', '')) else '',
                        responsible_person=str(row.get('负责人', '')) if pd.notna(row.get('负责人', '')) else '',
                        exception_type=str(row.get('异常类别', '')) if pd.notna(row.get('异常类别', '')) else '',
                        impact_cycle=str(row.get('影响周期', '')) if pd.notna(row.get('影响周期', '')) else '',
                        response_measures=str(row.get('应对措施', '')) if pd.notna(row.get('应对措施', '')) else ''
                    )
                    
                    db.session.add(milestone)
                    milestone_info = {
                        'project_id': project_id,
                        'project_name': project_name_str,
                        'milestone': milestone.milestone,
                        'responsible_department': milestone.responsible_department,
                        'planned_start_time': milestone.planned_start_time,
                        'planned_end_time': milestone.planned_end_time
                    }
                    imported_milestones.append(milestone_info)
                    
                    # 打印即将存储的里程碑数据
                    print(f"准备存储里程碑 - 项目ID: {project_id}, 项目名称: {project_name_str}, 里程碑: {milestone.milestone}")
                    
                except Exception as e:
                    failed_milestones.append({
                        'row': index + 1,
                        'data': row.to_dict(),
                        'error': str(e)
                    })
        
        # 提交事务
        print(f"正在提交数据到数据库...")
        db.session.commit()
        print(f"数据已成功提交到数据库")
        
        return {
            'success': True,
            'message': f'成功导入 {len(imported_milestones)} 个里程碑',
            'imported_milestones': imported_milestones,
            'failed_milestones': failed_milestones
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'导入里程碑失败: {str(e)}'
        }

def batch_import_projects_from_directory(directory_path):
    """
    批量导入目录中的所有Excel文件
    
    Args:
        directory_path (str): 包含Excel文件的目录路径
        
    Returns:
        dict: 批量导入结果
    """
    if not os.path.exists(directory_path):
        return {
            'success': False,
            'message': f'目录不存在: {directory_path}'
        }
    
    results = []
    total_success = 0
    total_failed = 0
    
    # 遍历目录中的所有Excel文件
    for filename in os.listdir(directory_path):
        if filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$'):
            file_path = os.path.join(directory_path, filename)
            print(f"正在处理文件: {filename}")
            
            result = import_projects_from_excel(file_path)
            result['file_name'] = filename
            results.append(result)
            
            if result['success']:
                total_success += len(result.get('imported_projects', []))
            else:
                total_failed += 1
    
    return {
        'success': True,
        'message': f'批量导入完成: 成功处理{total_success}个项目，{total_failed}个文件失败',
        'details': results
    }