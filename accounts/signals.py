# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import User, EmailVerificationCode

@receiver(post_save, sender=User) 
def send_otp_on_signup(sender, instance, created, **kwargs):
    print(f"--- SIGNAL TRIGGERED FOR {instance.email} ---")
    if created:
        # Forcing a print to see if 'created' is detected
        print(f"User created! is_active is: {instance.is_active}")
        
        if not instance.is_active:
            verification_record = EmailVerificationCode.objects.create(user=instance)
            verification_record.generate_code()
            
            html_content = render_to_string('email/verify_email.html', {'code': verification_record.code})
            
            send_mail(
                subject="Verify your Account",
                message=f"Your code is: {verification_record.code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                html_message=html_content,
                fail_silently=False
            )
            print("Email sent!")