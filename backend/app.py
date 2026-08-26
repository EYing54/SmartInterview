from app import create_app
from app.models import class_management, question, record, user  # noqa: F401

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
