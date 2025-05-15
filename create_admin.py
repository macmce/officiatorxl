import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'officiatorxl.settings')
django.setup()

from users.models import CustomUser

# Check if admin user already exists
if not CustomUser.objects.filter(username='admin').exists():
    # Create a superuser
    admin_user = CustomUser.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword123'
    )
    print(f"Admin user created: {admin_user.username}")
    print("Email: admin@example.com")
    print("Password: adminpassword123")
else:
    print("Admin user already exists")
