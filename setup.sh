#!/bin/bash
# Run this from the backend/ directory

echo "=== Tannu Tailoring Backend Setup ==="

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations tannu_backend
python manage.py migrate

# Create superuser (optional)
echo ""
echo "Create admin user? (y/n)"
read -r answer
if [ "$answer" = "y" ]; then
  python manage.py createsuperuser
fi

echo ""
echo "✅ Setup complete! Run: python manage.py runserver"
