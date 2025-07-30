#!/bin/bash

echo "🔧 Running init_env.py ..."
python init_env.py

echo "🧹 Collecting static files ..."
python manage.py collectstatic --noinput

echo "📦 Applying migrations ..."
python manage.py makemigrations
python manage.py makemigrations core
python manage.py makemigrations keyword_service
python manage.py makemigrations payment
python manage.py makemigrations project

python manage.py migrate

echo "⚙️ Creating superuser (if not exists) ..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin@1234');
else:
    print('Superuser already exists.')
"

echo "🚀 Starting Django server ..."
python manage.py runserver 0.0.0.0:8000
