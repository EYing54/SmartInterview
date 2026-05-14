from Database import app, db, User  # 引入要操作的内容

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        testuser = User(username="admin", password="123456", role=0)
        db.session.add(testuser)  # 告诉数据库我要往里面增加什么
        db.session.commit()  # 提交后才会正式添加到数据库里
        print("successful commit!")
