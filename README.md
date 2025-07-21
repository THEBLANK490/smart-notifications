# 🛎️ Smart Notification System

A Django-based backend for sending user notifications via in-app, mock email, and mock SMS channels, based on event triggers and user preferences.

---

## Setup Instructions

1. Clone the Repository
  git clone https://github.com/yourusername/smart-notifications.git
  cd smart-notifications


2. Create Virtual Environment & Install Dependencies 
  python -m venv venv
  source venv/bin/activate   # For Windows: venv\Scripts\activate
  pip install -r requirements.txt


3. Set Environment Variables
  DEBUG=True
  SECRET_KEY=your-secret-key
  DATABASE_URL=sqlite:///db.sqlite3
  CELERY_BROKER_URL=redis://localhost:6379/0


4. 🛠️ Run Migrations & Create Superuser
  python manage.py migrate
  python manage.py createsuperuser


