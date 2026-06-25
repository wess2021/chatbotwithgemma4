📦 E-Commerce Chatbot with AI
A Flask-based e-commerce chatbot powered by OpenRouter AI (Gemma 4). This chatbot can help customers with product inquiries, order tracking, shipping information, and general customer support.

✨ Features
🤖 AI-powered conversations using OpenRouter (Gemma 4)

💾 Persistent chat history with SQLite/MySQL database

🎨 Beautiful chat bubble UI

🌍 Multi-language support (English, French, Arabic)

🔒 Session management

📊 Chat analytics and history tracking

🛠️ Tech Stack
Backend: Flask 2.3.3

Database: SQLite (or MySQL)

AI: OpenRouter API (Google Gemma 4)

Frontend: HTML, CSS, JavaScript, Bootstrap

Session Management: Flask-Session

📋 Prerequisites
Python 3.8 or higher

pip (Python package manager)

Git (optional)

🚀 Installation Guide
Step 1: Clone or Download the Project
bash
# Clone the repository (if using git)
git clone <your-repo-url>
cd ecommerce-chatbot

# Or simply navigate to your project folder
cd ecommerce-chatbot
Step 2: Create and Activate Virtual Environment
Windows:
powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
Mac/Linux:
bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
Step 3: Install Dependencies
bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
Step 4: Set Up Environment Variables
Create a .env file in the root directory:

bash
# Create .env file (Windows)
type nul > .env

# Create .env file (Mac/Linux)
touch .env
Add the following to your .env file:

env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production-12345

# Database Configuration (SQLite - default)
DATABASE_URL=sqlite:///ecommerce.db

# OpenRouter API Configuration
# Get your API key from: https://openrouter.ai/account
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Choose AI Model (Free options)
# - google/gemma-4-31b-it:free  (Best, 31B parameters)
# - google/gemma-4-26b-a4b-it:free  (26B parameters, efficient)
# - openrouter/free  (Auto-selects best free model)
OPENROUTER_MODEL=google/gemma-4-31b-it:free

# Optional: Your website URL for OpenRouter
SITE_URL=http://localhost:5000

# Session Configuration
SESSION_TYPE=filesystem
SESSION_PERMANENT=False
SESSION_USE_SIGNER=True

# Application Configuration
DEBUG=True
CHAT_HISTORY_LIMIT=50
Step 5: Get OpenRouter API Key
Go to OpenRouter

Sign up or log in

Navigate to "API Keys" section

Click "Create API Key"

Name your key (e.g., "Chatbot")

Copy the key (starts with sk-or-v1-)

Paste it in your .env file as OPENROUTER_API_KEY

Step 6: Initialize Database
bash
# Run Python to create database tables
python -c "from app import create_app, db; from app.models.database import ChatSession, ChatMessage, ChatContext; app = create_app(); with app.app_context(): db.create_all(); print('✅ Database created successfully!')"
Or create a simple script init_db.py:

python
from app import create_app, db
from app.models.database import ChatSession, ChatMessage, ChatContext

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")
Run it:

bash
python init_db.py
Step 7: Test the Setup
bash
# Test environment variables
python test_load_env.py

# Test OpenRouter connection
python test_openrouter_fixed.py
Step 8: Run the Application
bash
# Start the Flask server
python run.py
Step 9: Access the Chatbot
Open your browser and navigate to:

text
http://localhost:5000
🎯 Using the Chatbot
Home Page: Visit the homepage to see the welcome screen

Chat Bubble: Click the chat bubble in the bottom-right corner

Start Chatting: Type your message and press Enter or click Send

Full Chat Page: Click "Open Chat" for a full-screen chat experience

Example Messages to Try:
"Hello" / "Bonjour" - Greeting

"What products do you have?" - Product inquiry

"I need help with my order" - Order support

"How much does shipping cost?" - Shipping information

"Can I return an item?" - Returns policy

🔧 Troubleshooting
Issue: ModuleNotFoundError: No module named 'flask'
Solution: Make sure your virtual environment is activated and install dependencies:

bash
pip install -r requirements.txt
Issue: OPENROUTER_API_KEY not found
Solution:

Check that .env file exists in the root directory

Verify OPENROUTER_API_KEY is set correctly

Run python test_load_env.py to debug

Issue: Port 5000 already in use
Solution: Change the port in run.py:

python
app.run(debug=True, host='0.0.0.0', port=5001)
Issue: Database errors
Solution: Delete the database file and recreate:

bash
# Windows
del ecommerce.db

# Mac/Linux
rm ecommerce.db

# Recreate
python init_db.py
Issue: OpenRouter rate limit
Solution: The app automatically uses fallback responses when rate-limited. Wait a few minutes and try again.

📁 Project Structure
text
ecommerce-chatbot/
├── app/
│   ├── __init__.py              # App initialization
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py              # Main routes
│   │   └── chat.py              # Chat API routes
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py          # Database models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_service.py    # AI service wrapper
│   │   └── openrouter_service.py # OpenRouter API service
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # Custom styles
│   │   ├── js/
│   │   │   └── chat.js          # Chat functionality
│   │   └── images/
│   └── templates/
│       ├── base.html            # Base template
│       ├── index.html           # Home page
│       ├── chat.html            # Full chat page
│       └── chat_bubble.html     # Chat widget
├── instance/                    # Instance folder (SQLite database)
├── .env                         # Environment variables (not in git)
├── .gitignore                   # Git ignore file
├── config.py                    # Configuration
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # This file
🚀 Deployment
Deploy to Production
Set environment variables:

bash
export FLASK_ENV=production
export DEBUG=False
export SECRET_KEY=your-very-secure-key
Use a production WSGI server:

bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
Use MySQL instead of SQLite:
Update DATABASE_URL in .env:

text
DATABASE_URL=mysql+pymysql://username:password@localhost/ecommerce
Set up SSL/HTTPS for production

🔒 Security Notes
NEVER commit your .env file to version control

Use strong SECRET_KEY in production

Enable HTTPS in production

Rate limit API calls to prevent abuse

Sanitize user input before processing

🤝 Contributing
Fork the repository

Create a feature branch

Commit your changes

Push to the branch

Create a Pull Request

📝 License
This project is open-source and available under the MIT License.

📧 Support
For support, please open an issue in the GitHub repository or contact the maintainer.

🎉 Acknowledgments
OpenRouter for providing AI API access

Google Gemma for the free AI model

Flask for the web framework

Happy Chatting! 🚀

Quick Start Commands
bash
# 1. Clone/Download project
cd ecommerce-chatbot

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file and add your OpenRouter API key
# OPENROUTER_API_KEY=sk-or-v1-your-key-here

# 5. Initialize database
python init_db.py

# 6. Run the application
python run.py

# 7. Open browser to http://localhost:5000
Note: Replace sk-or-v1-your-key-here with your actual OpenRouter API key. Get it from: https://openrouter.ai/account