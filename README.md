AI Task Manager

A Django-based task manager enhanced with AI for natural language processing, intelligent task creation, and productivity insights.

Features
AI-Powered Tools

Create tasks using natural language (e.g., "Call John tomorrow at 3pm, high priority").

Automatic extraction of title, due date, priority, and category.

Smart AI recommendations to boost productivity.

Task Management

Full CRUD: Create, Read, Update, Delete

Priorities: Urgent / High / Medium / Low

Categories & tags

Due dates and reminders

Track task progress and status

Analytics Dashboard

Interactive charts

Productivity insights

Task completion trends

AI-generated recommendations

User Management

Secure authentication

Personalized dashboards

Role-based features for future expansion

Quick Start
Clone the Repository
git clone https://github.com/yourusername/ai-task-manager.git
cd ai-task-manager

Create a Virtual Environment
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate

Install Dependencies
pip install -r requirements.txt

Configure Environment
cp .env.example .env
# Then edit .env and add your OpenAI API key

Run Migrations
python manage.py migrate

Create Admin User
python manage.py createsuperuser

Start the Server
python manage.py runserver


Visit: http://localhost:8000

Configuration
Required Environment Variables (.env)
SECRET_KEY=your-secret-key-here
DEBUG=True
OPENAI_API_KEY=sk-your-openai-key
DATABASE_URL=sqlite:///db.sqlite3

Optional Environment Variables
# Email Notifications
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Production Settings
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

How It Works
AI Features

Quickly add tasks using natural sentences

Automatic parsing and categorization

AI-driven productivity suggestions

Task Features

Manual or AI-assisted task creation

Set priorities & categories

Due date reminders

Track status and progress

Dashboard

View task statistics and charts

Monitor performance trends

Receive AI suggestions
