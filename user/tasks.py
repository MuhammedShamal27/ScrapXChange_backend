# user/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import CustomUser, UserProfile
import random
import logging

# Set up logger
logger = logging.getLogger(__name__)

@shared_task(name='send_otp_email')  # Add explicit name
def generate_and_send_otp(user_email):
    try:
        # Generate OTP
        otp = str(random.randint(1000, 9999))
        print("\n" + "="*50)
        print(f"🔐 NEW OTP GENERATED")
        print(f"📧 Email: {user_email}")
        print(f"🔑 OTP: {otp}")
        print("\n" + "="*50)
        # Get user and profile
        user = CustomUser.objects.get(email=user_email)
        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        
        # Update OTP
        user_profile.otp = otp
        user_profile.otp_generated_at = timezone.now()
        user_profile.save()
        
        # Send email
        subject = 'Welcome to ScrapXChange! - User Verification Mail'
        message = f'Your OTP Code is {otp}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user_email]
        
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False
        )
        
        return f"OTP sent successfully to the given {user_email} and the {otp}"
    
    except CustomUser.DoesNotExist:
        return f"Error: User with email {user_email} does not exist."
    except Exception as e:
        return f"Error sending OTP: {str(e)}"