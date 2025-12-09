from app import db, SysClub, app

def test_sys_club_table():
    with app.app_context():
        # 检查sys_club表中的记录数
        count = SysClub.query.count()
        print(f"sys_club表中的记录数: {count}")
        print("sys_club表已成功创建并可访问")

if __name__ == "__main__":
    test_sys_club_table()