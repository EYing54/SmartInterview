from app import create_app
from app.models import question, record, class_management, user
from extensions import db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
