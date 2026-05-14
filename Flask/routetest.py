from Database import app, db, User


@app.route("/add")
def add_uesr_from_web():
    adduser = User(username="20260514", password="123456", role=1)
    db.session.add(adduser)
    db.session.commit()
    return "successful commit"


if __name__ == "__main__":
    app.run(debug=True)
