from app import create_app
from app.models import question, record, class_management, user  # noqa: F401

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
