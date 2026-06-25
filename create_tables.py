from app import create_app, db
from app.models.database import ChatSession, ChatMessage, ChatContext

app = create_app()

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("✅ Tables created successfully!")
    print("Tables created:")
    print("  - chat_sessions")
    print("  - chat_messages")
    print("  - chat_context")