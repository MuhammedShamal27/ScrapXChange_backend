from django.core.mail import send_mail
from django.conf import settings
from user.models import CustomUser
import random

def generate_otp():
    return random.randint(1000,9999)

def send_otp_via_email(email,otp):
    subject='Welcome to ScrapXChange ! -User Verification Mail'
    message=f'Your OTP Code is {otp}'
    email_from=settings.EMAIL_HOST_USER
    try:
        send_mail(subject,message,email_from,[email])
        user_obj = CustomUser.objects.get(email=email)
        user_obj.otp=otp
        user_obj.save()
        print(f"OTP sent successfully to {email} from generte otp")
        print(otp)
    except Exception as e:
        print (f"Error sending OTP to {email}:{e}")